from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from django.db.models import Q, Sum, Avg, Max, Min
from django.utils import timezone
from datetime import timedelta
import logging

from .models import Host, ProcessSnapshot, Process, ProcessRelationship, SystemMetrics
from .serializers import (
    HostSerializer, ProcessSerializer, ProcessSnapshotSerializer,
    ProcessSnapshotSummarySerializer, ProcessRelationshipSerializer,
    SystemMetricsSerializer, ProcessTreeSerializer, ProcessDataSubmissionSerializer,
    ProcessSearchSerializer, HostSummarySerializer
)

logger = logging.getLogger(__name__)


class APIKeyPermission(permissions.BasePermission):
    """
    Custom permission class for API key authentication
    """
    def has_permission(self, request, view):
        # Skip API key check for certain actions
        if view.action in ['list', 'retrieve']:
            return True
        
        # Check API key in headers
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return False
        
        # Compare with settings API key
        from django.conf import settings
        return api_key == settings.API_KEY


class PublicReadPermission(permissions.BasePermission):
    """
    Permission class that allows public read access
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False


class HostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Host model
    """
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = [PublicReadPermission]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        queryset = Host.objects.all()
        
        # Filter by platform
        platform = self.request.query_params.get('platform', None)
        if platform:
            queryset = queryset.filter(platform__iexact=platform)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter by hostname
        hostname = self.request.query_params.get('hostname', None)
        if hostname:
            queryset = queryset.filter(hostname__icontains=hostname)
        
        return queryset.order_by('-last_seen')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary of all hosts"""
        hosts = self.get_queryset()
        serializer = HostSummarySerializer(hosts, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def processes(self, request, pk=None):
        """Get all processes for a specific host"""
        host = self.get_object()
        latest_snapshot = host.snapshots.first()
        
        if not latest_snapshot:
            return Response({'message': 'No process data available for this host'}, 
                          status=status.HTTP_404_NOT_FOUND)
        
        processes = latest_snapshot.processes.all()
        serializer = ProcessSerializer(processes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def snapshots(self, request, pk=None):
        """Get all snapshots for a specific host"""
        host = self.get_object()
        snapshots = host.snapshots.all()
        serializer = ProcessSnapshotSummarySerializer(snapshots, many=True)
        return Response(serializer.data)


class ProcessSnapshotViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProcessSnapshot model
    """
    queryset = ProcessSnapshot.objects.all()
    serializer_class = ProcessSnapshotSerializer
    permission_classes = [PublicReadPermission]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        queryset = ProcessSnapshot.objects.select_related('host').prefetch_related('processes')
        
        # Filter by host
        hostname = self.request.query_params.get('hostname', None)
        if hostname:
            queryset = queryset.filter(host__hostname__icontains=hostname)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest snapshot for each host"""
        hosts = Host.objects.filter(is_active=True)
        latest_snapshots = []
        
        for host in hosts:
            latest = host.snapshots.first()
            if latest:
                serializer = ProcessSnapshotSummarySerializer(latest)
                latest_snapshots.append(serializer.data)
        
        return Response(latest_snapshots)
    
    @action(detail=True, methods=['get'])
    def tree(self, request, pk=None):
        """Get process tree structure for a snapshot"""
        snapshot = self.get_object()
        processes = snapshot.processes.all()
        
        # Build process tree
        process_tree = self._build_process_tree(processes)
        return Response(process_tree)
    
    def _build_process_tree(self, processes):
        """Build hierarchical process tree"""
        # Create a dictionary of processes by PID
        process_dict = {p.pid: p for p in processes}
        root_processes = []
        
        for process in processes:
            if not process.ppid or process.ppid not in process_dict:
                # This is a root process
                root_processes.append(self._build_tree_node(process, process_dict))
        
        return root_processes
    
    def _build_tree_node(self, process, process_dict, level=0):
        """Build a single tree node with children"""
        node = {
            'process': ProcessSerializer(process).data,
            'level': level,
            'children': [],
            'is_expanded': False
        }
        
        # Find child processes
        children = [p for p in process_dict.values() if p.ppid == process.pid]
        for child in children:
            child_node = self._build_tree_node(child, process_dict, level + 1)
            node['children'].append(child_node)
        
        return node


class ProcessViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Process model
    """
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    permission_classes = [PublicReadPermission]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        queryset = Process.objects.select_related('snapshot__host')
        
        # Filter by snapshot
        snapshot_id = self.request.query_params.get('snapshot', None)
        if snapshot_id:
            queryset = queryset.filter(snapshot_id=snapshot_id)
        
        # Filter by host
        hostname = self.request.query_params.get('hostname', None)
        if hostname:
            queryset = queryset.filter(snapshot__host__hostname__icontains=hostname)
        
        # Filter by process name
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by CPU usage
        min_cpu = self.request.query_params.get('min_cpu', None)
        max_cpu = self.request.query_params.get('max_cpu', None)
        
        if min_cpu:
            queryset = queryset.filter(cpu_percent__gte=float(min_cpu))
        if max_cpu:
            queryset = queryset.filter(cpu_percent__lte=float(max_cpu))
        
        # Filter by memory usage
        min_memory = self.request.query_params.get('min_memory', None)
        max_memory = self.request.query_params.get('max_memory', None)
        
        if min_memory:
            queryset = queryset.filter(memory_rss__gte=int(min_memory))
        if max_memory:
            queryset = queryset.filter(memory_rss__lte=int(max_memory))
        
        return queryset.order_by('-cpu_percent', '-memory_percent')
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search processes with advanced filtering"""
        serializer = ProcessSearchSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        queryset = self.get_queryset()
        
        # Apply search filters
        if data.get('hostname'):
            queryset = queryset.filter(snapshot__host__hostname__icontains=data['hostname'])
        
        if data.get('process_name'):
            queryset = queryset.filter(name__icontains=data['process_name'])
        
        if data.get('status'):
            queryset = queryset.filter(status=data['status'])
        
        if data.get('username'):
            queryset = queryset.filter(username__icontains=data['username'])
        
        # Apply pagination
        limit = data.get('limit', 100)
        offset = data.get('offset', 0)
        queryset = queryset[offset:offset + limit]
        
        serializer = ProcessSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_cpu(self, request):
        """Get top CPU consuming processes"""
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_queryset().order_by('-cpu_percent')[:limit]
        serializer = ProcessSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_memory(self, request):
        """Get top memory consuming processes"""
        limit = int(request.query_params.get('limit', 10))
        queryset = self.get_queryset().order_by('-memory_rss')[:limit]
        serializer = ProcessSerializer(queryset, many=True)
        return Response(serializer.data)


class ProcessDataSubmissionViewSet(viewsets.ViewSet):
    """
    ViewSet for receiving process data from agents
    """
    permission_classes = [APIKeyPermission]
    authentication_classes = [TokenAuthentication]
    
    def create(self, request):
        """Receive process data from agent"""
        serializer = ProcessDataSubmissionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            data = serializer.validated_data
            
            # Get or create host
            host, created = Host.objects.get_or_create(
                hostname=data['hostname'],
                defaults={
                    'platform': data.get('platform', 'Unknown'),
                    'architecture': data.get('architecture', 'Unknown'),
                    'cpu_count': data.get('cpu_count'),
                    'total_memory': data.get('total_memory'),
                    'os_info': data.get('os_info', ''),
                    'ip_address': data.get('ip_address'),
                }
            )
            
            # Update host information if not newly created
            if not created:
                host.platform = data.get('platform', host.platform)
                host.architecture = data.get('architecture', host.architecture)
                host.cpu_count = data.get('cpu_count', host.cpu_count)
                host.total_memory = data.get('total_memory', host.total_memory)
                host.os_info = data.get('os_info', host.os_info)
                host.ip_address = data.get('ip_address', host.ip_address)
                host.last_seen = timezone.now()
                host.save()
            
            # Create process snapshot
            total_cpu = sum(p.get('cpu_percent', 0) for p in data['processes'])
            total_memory = sum(p.get('memory_rss', 0) for p in data['processes'])
            
            snapshot = ProcessSnapshot.objects.create(
                host=host,
                total_processes=len(data['processes']),
                total_cpu_percent=total_cpu,
                total_memory_mb=total_memory / (1024 * 1024),  # Convert to MB
                system_cpu_percent=data.get('system_cpu_percent'),
                system_memory_percent=data.get('system_memory_percent'),
            )
            
            # Create process records
            processes = []
            for proc_data in data['processes']:
                process = Process(
                    snapshot=snapshot,
                    pid=proc_data['pid'],
                    ppid=proc_data.get('ppid'),
                    name=proc_data['name'],
                    exe=proc_data.get('exe', ''),
                    cmdline=proc_data.get('cmdline', ''),
                    status=proc_data.get('status', 'unknown'),
                    cpu_percent=proc_data.get('cpu_percent', 0.0),
                    memory_rss=proc_data.get('memory_rss', 0),
                    memory_vms=proc_data.get('memory_vms', 0),
                    memory_percent=proc_data.get('memory_percent', 0.0),
                    create_time=proc_data.get('create_time'),
                    num_threads=proc_data.get('num_threads'),
                    nice=proc_data.get('nice'),
                    username=proc_data.get('username', ''),
                    working_set=proc_data.get('working_set'),
                    private_bytes=proc_data.get('private_bytes'),
                )
                processes.append(process)
            
            # Bulk create processes
            Process.objects.bulk_create(processes)
            
            logger.info(f"Process data received from {host.hostname}: {len(processes)} processes")
            
            return Response({
                'message': 'Process data received successfully',
                'host_id': str(host.id),
                'snapshot_id': str(snapshot.id),
                'processes_count': len(processes)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error processing agent data: {str(e)}")
            return Response({
                'error': 'Internal server error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SystemMetricsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SystemMetrics model
    """
    queryset = SystemMetrics.objects.all()
    serializer_class = SystemMetricsSerializer
    permission_classes = [PublicReadPermission]
    authentication_classes = [TokenAuthentication]
    
    def get_queryset(self):
        queryset = SystemMetrics.objects.select_related('host')
        
        # Filter by host
        hostname = self.request.query_params.get('hostname', None)
        if hostname:
            queryset = queryset.filter(host__hostname__icontains=hostname)
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest system metrics for each host"""
        hosts = Host.objects.filter(is_active=True)
        latest_metrics = []
        
        for host in hosts:
            latest = host.system_metrics.first()
            if latest:
                serializer = SystemMetricsSerializer(latest)
                latest_metrics.append(serializer.data)
        
        return Response(latest_metrics)
