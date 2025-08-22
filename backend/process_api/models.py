from django.db import models
from django.utils import timezone
import uuid


class Host(models.Model):
    """
    Represents a machine that sends process data
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hostname = models.CharField(max_length=255, unique=True, help_text="Machine hostname")
    ip_address = models.GenericIPAddressField(null=True, blank=True, help_text="Machine IP address")
    os_info = models.CharField(max_length=255, blank=True, help_text="Operating system information")
    platform = models.CharField(max_length=50, blank=True, help_text="Platform (Windows, macOS, Linux)")
    architecture = models.CharField(max_length=20, blank=True, help_text="System architecture (x86_64, arm64, etc.)")
    cpu_count = models.IntegerField(null=True, blank=True, help_text="Number of CPU cores")
    total_memory = models.BigIntegerField(null=True, blank=True, help_text="Total memory in bytes")
    is_active = models.BooleanField(default=True, help_text="Whether the host is currently active")
    first_seen = models.DateTimeField(auto_now_add=True, help_text="When this host was first seen")
    last_seen = models.DateTimeField(auto_now=True, help_text="When this host was last seen")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hosts'
        ordering = ['-last_seen']
        verbose_name = 'Host'
        verbose_name_plural = 'Hosts'

    def __str__(self):
        return f"{self.hostname} ({self.platform})"

    @property
    def total_memory_gb(self):
        """Return total memory in GB"""
        if self.total_memory is not None:
            return round(self.total_memory / (1024**3), 2)
        return 0.0

    @property
    def uptime_hours(self):
        """Return uptime in hours since first seen"""
        if self.first_seen:
            delta = timezone.now() - self.first_seen
            return round(delta.total_seconds() / 3600, 2)
        return 0


class ProcessSnapshot(models.Model):
    """
    Represents a snapshot of all processes at a specific time
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='snapshots')
    timestamp = models.DateTimeField(auto_now_add=True, help_text="When this snapshot was taken")
    total_processes = models.IntegerField(help_text="Total number of processes in this snapshot")
    total_cpu_percent = models.FloatField(default=0.0, help_text="Total CPU usage percentage")
    total_memory_mb = models.FloatField(default=0.0, help_text="Total memory usage in MB")
    system_cpu_percent = models.FloatField(null=True, blank=True, help_text="System CPU usage percentage")
    system_memory_percent = models.FloatField(null=True, blank=True, help_text="System memory usage percentage")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'process_snapshots'
        ordering = ['-timestamp']
        verbose_name = 'Process Snapshot'
        verbose_name_plural = 'Process Snapshots'
        indexes = [
            models.Index(fields=['host', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        return f"Snapshot for {self.host.hostname} at {self.timestamp}"

    @property
    def total_memory_gb(self):
        """Return total memory in GB"""
        return round(self.total_memory_mb / 1024, 2)


class Process(models.Model):
    """
    Represents a single process in a snapshot
    """
    STATUS_CHOICES = [
        ('running', 'Running'),
        ('sleeping', 'Sleeping'),
        ('disk-sleep', 'Disk Sleep'),
        ('stopped', 'Stopped'),
        ('zombie', 'Zombie'),
        ('unknown', 'Unknown'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    snapshot = models.ForeignKey(ProcessSnapshot, on_delete=models.CASCADE, related_name='processes')
    pid = models.IntegerField(help_text="Process ID")
    ppid = models.IntegerField(null=True, blank=True, help_text="Parent Process ID")
    name = models.CharField(max_length=255, help_text="Process name")
    exe = models.CharField(max_length=500, blank=True, help_text="Executable path")
    cmdline = models.TextField(blank=True, help_text="Command line arguments")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')
    cpu_percent = models.FloatField(default=0.0, help_text="CPU usage percentage")
    memory_rss = models.BigIntegerField(default=0, help_text="Resident Set Size in bytes")
    memory_vms = models.BigIntegerField(default=0, help_text="Virtual Memory Size in bytes")
    memory_percent = models.FloatField(default=0.0, help_text="Memory usage percentage")
    create_time = models.FloatField(null=True, blank=True, help_text="Process creation time (timestamp)")
    num_threads = models.IntegerField(null=True, blank=True, help_text="Number of threads")
    nice = models.IntegerField(null=True, blank=True, help_text="Process nice value")
    username = models.CharField(max_length=100, blank=True, help_text="Username running the process")
    working_set = models.BigIntegerField(null=True, blank=True, help_text="Working set size (Windows)")
    private_bytes = models.BigIntegerField(null=True, blank=True, help_text="Private bytes (Windows)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'processes'
        ordering = ['-cpu_percent', '-memory_percent']
        verbose_name = 'Process'
        verbose_name_plural = 'Processes'
        indexes = [
            models.Index(fields=['snapshot', 'pid']),
            models.Index(fields=['snapshot', 'ppid']),
            models.Index(fields=['name']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.name} (PID: {self.pid})"

    @property
    def memory_rss_mb(self):
        """Return RSS memory in MB"""
        return round(self.memory_rss / (1024**2), 2)

    @property
    def memory_vms_mb(self):
        """Return VMS memory in MB"""
        return round(self.memory_vms / (1024**2), 2)

    @property
    def uptime_seconds(self):
        """Return process uptime in seconds"""
        if self.create_time:
            import time
            return int(time.time() - self.create_time)
        return 0

    @property
    def parent_process(self):
        """Get the parent process if it exists in the same snapshot"""
        if self.ppid:
            return self.snapshot.processes.filter(pid=self.ppid).first()
        return None

    @property
    def child_processes(self):
        """Get all child processes in the same snapshot"""
        return self.snapshot.processes.filter(ppid=self.pid)


class ProcessRelationship(models.Model):
    """
    Represents parent-child relationships between processes
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    snapshot = models.ForeignKey(ProcessSnapshot, on_delete=models.CASCADE, related_name='relationships')
    parent_process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='parent_relationships')
    child_process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='child_relationships')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'process_relationships'
        unique_together = ['snapshot', 'parent_process', 'child_process']
        verbose_name = 'Process Relationship'
        verbose_name_plural = 'Process Relationships'

    def __str__(self):
        return f"{self.parent_process.name} -> {self.child_process.name}"


class SystemMetrics(models.Model):
    """
    Additional system metrics for monitoring
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(Host, on_delete=models.CASCADE, related_name='system_metrics')
    timestamp = models.DateTimeField(auto_now_add=True)
    cpu_count = models.IntegerField(help_text="Number of CPU cores")
    cpu_freq_current = models.FloatField(null=True, blank=True, help_text="Current CPU frequency in MHz")
    cpu_freq_min = models.FloatField(null=True, blank=True, help_text="Minimum CPU frequency in MHz")
    cpu_freq_max = models.FloatField(null=True, blank=True, help_text="Maximum CPU frequency in MHz")
    memory_total = models.BigIntegerField(help_text="Total memory in bytes")
    memory_available = models.BigIntegerField(help_text="Available memory in bytes")
    memory_used = models.BigIntegerField(help_text="Used memory in bytes")
    memory_free = models.BigIntegerField(help_text="Free memory in bytes")
    memory_percent = models.FloatField(help_text="Memory usage percentage")
    disk_usage = models.JSONField(default=dict, help_text="Disk usage information")
    network_io = models.JSONField(default=dict, help_text="Network I/O statistics")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'system_metrics'
        ordering = ['-timestamp']
        verbose_name = 'System Metrics'
        verbose_name_plural = 'System Metrics'

    def __str__(self):
        return f"System metrics for {self.host.hostname} at {self.timestamp}"

    @property
    def memory_total_gb(self):
        """Return total memory in GB"""
        return round(self.memory_total / (1024**3), 2)

    @property
    def memory_available_gb(self):
        """Return available memory in GB"""
        return round(self.memory_available / (1024**3), 2) 