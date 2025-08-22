from rest_framework import serializers
from .models import Host, ProcessSnapshot, Process, ProcessRelationship, SystemMetrics


class HostSerializer(serializers.ModelSerializer):
    """Serializer for Host model"""
    total_memory_gb = serializers.ReadOnlyField()
    uptime_hours = serializers.ReadOnlyField()
    
    class Meta:
        model = Host
        fields = [
            'id', 'hostname', 'ip_address', 'os_info', 'platform', 'architecture',
            'cpu_count', 'total_memory', 'total_memory_gb', 'is_active',
            'first_seen', 'last_seen', 'created_at', 'updated_at', 'uptime_hours'
        ]
        read_only_fields = ['id', 'first_seen', 'last_seen', 'created_at', 'updated_at']


class ProcessSerializer(serializers.ModelSerializer):
    """Serializer for Process model"""
    memory_rss_mb = serializers.ReadOnlyField()
    memory_vms_mb = serializers.ReadOnlyField()
    uptime_seconds = serializers.ReadOnlyField()
    parent_process_name = serializers.SerializerMethodField()
    child_processes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Process
        fields = [
            'id', 'snapshot', 'pid', 'ppid', 'name', 'exe', 'cmdline', 'status',
            'cpu_percent', 'memory_rss', 'memory_rss_mb', 'memory_vms', 'memory_vms_mb',
            'memory_percent', 'create_time', 'num_threads', 'nice', 'username',
            'working_set', 'private_bytes', 'created_at', 'parent_process_name',
            'child_processes_count', 'uptime_seconds'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_parent_process_name(self, obj):
        """Get parent process name if it exists"""
        if obj.ppid and hasattr(obj, 'snapshot'):
            parent = obj.snapshot.processes.filter(pid=obj.ppid).first()
            return parent.name if parent else None
        return None
    
    def get_child_processes_count(self, obj):
        """Get count of child processes"""
        if hasattr(obj, 'snapshot'):
            return obj.snapshot.processes.filter(ppid=obj.pid).count()
        return 0


class ProcessSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for ProcessSnapshot model"""
    total_memory_gb = serializers.ReadOnlyField()
    host = HostSerializer(read_only=True)
    processes = ProcessSerializer(many=True, read_only=True)
    processes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProcessSnapshot
        fields = [
            'id', 'host', 'timestamp', 'total_processes', 'total_cpu_percent',
            'total_memory_mb', 'total_memory_gb', 'system_cpu_percent',
            'system_memory_percent', 'created_at', 'processes', 'processes_count'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at']
    
    def get_processes_count(self, obj):
        """Get actual count of processes"""
        return obj.processes.count()


class ProcessSnapshotSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for ProcessSnapshot (without processes)"""
    total_memory_gb = serializers.ReadOnlyField()
    host = HostSerializer(read_only=True)
    
    class Meta:
        model = ProcessSnapshot
        fields = [
            'id', 'host', 'timestamp', 'total_processes', 'total_cpu_percent',
            'total_memory_mb', 'total_memory_gb', 'system_cpu_percent',
            'system_memory_percent', 'created_at'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at']


class ProcessRelationshipSerializer(serializers.ModelSerializer):
    """Serializer for ProcessRelationship model"""
    parent_process_name = serializers.CharField(source='parent_process.name', read_only=True)
    child_process_name = serializers.CharField(source='child_process.name', read_only=True)
    
    class Meta:
        model = ProcessRelationship
        fields = [
            'id', 'snapshot', 'parent_process', 'child_process',
            'parent_process_name', 'child_process_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SystemMetricsSerializer(serializers.ModelSerializer):
    """Serializer for SystemMetrics model"""
    memory_total_gb = serializers.ReadOnlyField()
    memory_available_gb = serializers.ReadOnlyField()
    host = HostSerializer(read_only=True)
    
    class Meta:
        model = SystemMetrics
        fields = [
            'id', 'host', 'timestamp', 'cpu_count', 'cpu_freq_current',
            'cpu_freq_min', 'cpu_freq_max', 'memory_total', 'memory_total_gb',
            'memory_available', 'memory_available_gb', 'memory_used',
            'memory_free', 'memory_percent', 'disk_usage', 'network_io', 'created_at'
        ]
        read_only_fields = ['id', 'timestamp', 'created_at']


class ProcessTreeSerializer(serializers.Serializer):
    """Serializer for process tree structure"""
    process = ProcessSerializer()
    children = serializers.ListField(child=serializers.DictField(), required=False)
    level = serializers.IntegerField(default=0)
    is_expanded = serializers.BooleanField(default=False)


class ProcessDataSubmissionSerializer(serializers.Serializer):
    """Serializer for receiving process data from agent"""
    hostname = serializers.CharField(max_length=255)
    platform = serializers.CharField(max_length=50, required=False)
    architecture = serializers.CharField(max_length=20, required=False)
    cpu_count = serializers.IntegerField(required=False)
    total_memory = serializers.IntegerField(required=False)
    os_info = serializers.CharField(max_length=255, required=False)
    ip_address = serializers.CharField(required=False)
    
    # System metrics
    system_cpu_percent = serializers.FloatField(required=False)
    system_memory_percent = serializers.FloatField(required=False)
    
    # Process data
    processes = serializers.ListField(
        child=serializers.DictField(),
        min_length=1
    )
    
    def validate_processes(self, value):
        """Validate process data structure"""
        required_fields = ['pid', 'name', 'cpu_percent', 'memory_rss']
        
        for process in value:
            if not isinstance(process, dict):
                raise serializers.ValidationError("Each process must be a dictionary")
            
            for field in required_fields:
                if field not in process:
                    raise serializers.ValidationError(f"Process missing required field: {field}")
            
            # Validate PID is positive integer
            try:
                pid = int(process['pid'])
                if pid <= 0:
                    raise serializers.ValidationError("PID must be a positive integer")
            except (ValueError, TypeError):
                raise serializers.ValidationError("PID must be a valid integer")
        
        return value


class ProcessSearchSerializer(serializers.Serializer):
    """Serializer for process search parameters"""
    hostname = serializers.CharField(required=False)
    process_name = serializers.CharField(required=False)
    min_cpu = serializers.FloatField(required=False, min_value=0.0, max_value=100.0)
    max_cpu = serializers.FloatField(required=False, min_value=0.0, max_value=100.0)
    min_memory = serializers.FloatField(required=False, min_value=0.0)
    max_memory = serializers.FloatField(required=False, min_value=0.0)
    status = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    limit = serializers.IntegerField(required=False, min_value=1, max_value=1000, default=100)
    offset = serializers.IntegerField(required=False, min_value=0, default=0)


class HostSummarySerializer(serializers.ModelSerializer):
    """Simplified serializer for host summary"""
    total_memory_gb = serializers.ReadOnlyField()
    uptime_hours = serializers.ReadOnlyField()
    latest_snapshot = serializers.SerializerMethodField()
    process_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Host
        fields = [
            'id', 'hostname', 'platform', 'architecture', 'cpu_count',
            'total_memory_gb', 'is_active', 'last_seen', 'uptime_hours',
            'latest_snapshot', 'process_count'
        ]
    
    def get_latest_snapshot(self, obj):
        """Get the latest snapshot for this host"""
        latest = obj.snapshots.first()
        if latest:
            return {
                'timestamp': latest.timestamp,
                'total_processes': latest.total_processes,
                'total_cpu_percent': latest.total_cpu_percent,
                'total_memory_mb': latest.total_memory_mb
            }
        return None
    
    def get_process_count(self, obj):
        """Get the current process count for this host"""
        latest = obj.snapshots.first()
        return latest.total_processes if latest else 0
