from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Host, ProcessSnapshot, Process, ProcessRelationship, SystemMetrics


@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = [
        'hostname', 'platform', 'architecture', 'cpu_count', 
        'total_memory_gb', 'is_active', 'last_seen', 'uptime_hours'
    ]
    list_filter = ['platform', 'architecture', 'is_active', 'first_seen', 'last_seen']
    search_fields = ['hostname', 'ip_address', 'os_info']
    readonly_fields = ['id', 'first_seen', 'last_seen', 'created_at', 'updated_at']
    ordering = ['-last_seen']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('hostname', 'ip_address', 'os_info', 'platform', 'architecture')
        }),
        ('System Information', {
            'fields': ('cpu_count', 'total_memory', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('first_seen', 'last_seen', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def total_memory_gb(self, obj):
        return f"{obj.total_memory_gb} GB" if obj.total_memory_gb else "N/A"
    total_memory_gb.short_description = "Total Memory (GB)"
    
    def uptime_hours(self, obj):
        return f"{obj.uptime_hours} hours"
    uptime_hours.short_description = "Uptime"


@admin.register(ProcessSnapshot)
class ProcessSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        'host', 'timestamp', 'total_processes', 'total_cpu_percent', 
        'total_memory_gb', 'system_cpu_percent', 'system_memory_percent'
    ]
    list_filter = ['timestamp', 'host__platform', 'host__is_active']
    search_fields = ['host__hostname']
    readonly_fields = ['id', 'timestamp', 'created_at']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('Snapshot Information', {
            'fields': ('host', 'timestamp', 'total_processes')
        }),
        ('System Metrics', {
            'fields': ('total_cpu_percent', 'total_memory_mb', 'system_cpu_percent', 'system_memory_percent')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def total_memory_gb(self, obj):
        return f"{obj.total_memory_gb} GB"
    total_memory_gb.short_description = "Total Memory (GB)"


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'pid', 'ppid', 'username', 'status', 'cpu_percent', 
        'memory_rss_mb', 'memory_vms_mb', 'snapshot_host', 'snapshot_time'
    ]
    list_filter = ['status', 'snapshot__host__platform', 'snapshot__timestamp']
    search_fields = ['name', 'username', 'snapshot__host__hostname']
    readonly_fields = ['id', 'created_at']
    ordering = ['-cpu_percent', '-memory_rss']
    
    fieldsets = (
        ('Process Information', {
            'fields': ('snapshot', 'pid', 'ppid', 'name', 'exe', 'cmdline', 'status')
        }),
        ('Resource Usage', {
            'fields': ('cpu_percent', 'memory_rss', 'memory_vms', 'memory_percent')
        }),
        ('Additional Information', {
            'fields': ('create_time', 'num_threads', 'nice', 'username', 'working_set', 'private_bytes')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def snapshot_host(self, obj):
        return obj.snapshot.host.hostname
    snapshot_host.short_description = "Host"
    
    def snapshot_time(self, obj):
        return obj.snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    snapshot_time.short_description = "Snapshot Time"
    
    def memory_rss_mb(self, obj):
        return f"{obj.memory_rss_mb} MB"
    memory_rss_mb.short_description = "Memory RSS (MB)"
    
    def memory_vms_mb(self, obj):
        return f"{obj.memory_vms_mb} MB"
    memory_vms_mb.short_description = "Memory VMS (MB)"


@admin.register(ProcessRelationship)
class ProcessRelationshipAdmin(admin.ModelAdmin):
    list_display = ['parent_process_name', 'child_process_name', 'snapshot_host', 'snapshot_time']
    list_filter = ['snapshot__host__platform', 'snapshot__timestamp']
    search_fields = ['parent_process__name', 'child_process__name', 'snapshot__host__hostname']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Relationship Information', {
            'fields': ('snapshot', 'parent_process', 'child_process')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def parent_process_name(self, obj):
        return obj.parent_process.name
    parent_process_name.short_description = "Parent Process"
    
    def child_process_name(self, obj):
        return obj.child_process.name
    child_process_name.short_description = "Child Process"
    
    def snapshot_host(self, obj):
        return obj.snapshot.host.hostname
    snapshot_host.short_description = "Host"
    
    def snapshot_time(self, obj):
        return obj.snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    snapshot_time.short_description = "Snapshot Time"


@admin.register(SystemMetrics)
class SystemMetricsAdmin(admin.ModelAdmin):
    list_display = [
        'host', 'timestamp', 'cpu_count', 'memory_total_gb', 'memory_percent',
        'cpu_freq_current'
    ]
    list_filter = ['timestamp', 'host__platform', 'host__is_active']
    search_fields = ['host__hostname']
    readonly_fields = ['id', 'timestamp', 'created_at']
    ordering = ['-timestamp']
    
    fieldsets = (
        ('System Information', {
            'fields': ('host', 'timestamp', 'cpu_count')
        }),
        ('CPU Information', {
            'fields': ('cpu_freq_current', 'cpu_freq_min', 'cpu_freq_max')
        }),
        ('Memory Information', {
            'fields': ('memory_total', 'memory_available', 'memory_used', 'memory_free', 'memory_percent')
        }),
        ('Additional Metrics', {
            'fields': ('disk_usage', 'network_io'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def memory_total_gb(self, obj):
        return f"{obj.memory_total_gb} GB"
    memory_total_gb.short_description = "Total Memory (GB)"


# Customize admin site
admin.site.site_header = "Process Monitor Administration"
admin.site.site_title = "Process Monitor Admin"
admin.site.index_title = "Welcome to Process Monitor Administration"
