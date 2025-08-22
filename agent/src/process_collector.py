"""
Process Collector Module
Collects process information from the local system using psutil
"""

import psutil
import time
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime


class ProcessCollector:
    """
    Collects process information from the local system
    """
    
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.last_collection_time = None
        self.config = config
        
        # Process names to filter out (privacy/security)
        self.filtered_processes = set()
        if config and config.enable_process_filtering:
            for name in config.filtered_process_names:
                self.filtered_processes.add(name.strip().lower())
                # Also add common variations
                if 'cursor' in name.lower():
                    self.filtered_processes.update([
                        'cursor', 'cursor helper', 'cursor helper (gpu)', 'cursor helper (renderer)', 
                        'cursor helper (plugin)', 'cursor helper (utility)', 'cursor helper (network)',
                        'cursor helper (extension)', 'cursor helper (extension-host)',
                        'cursor helper (gpu-process)', 'cursor helper (renderer-process)',
                        'cursor helper (plugin-process)', 'cursor helper (utility-process)',
                        'cursor helper (network-process)', 'cursor helper (extension-process)',
                        'cursor helper (extension-host-process)'
                    ])
        
    def collect_all_processes(self) -> List[Dict[str, Any]]:
        """
        Collect information about all running processes
        
        Returns:
            List of process dictionaries
        """
        try:
            processes = []
            
            # Get all processes
            for proc in psutil.process_iter(['pid', 'name', 'ppid', 'status', 'create_time']):
                try:
                    process_info = self.collect_process_info(proc)
                    if process_info:
                        processes.append(process_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    # Skip processes that can't be accessed
                    continue
                except Exception as e:
                    self.logger.warning(f"Error collecting info for process {proc.pid}: {e}")
                    continue
            
            self.last_collection_time = time.time()
            self.logger.info(f"Collected information for {len(processes)} processes")
            
            return processes
            
        except Exception as e:
            self.logger.error(f"Error collecting processes: {e}")
            return []
    
    def collect_process_info(self, proc: psutil.Process) -> Optional[Dict[str, Any]]:
        """
        Collect detailed information about a single process
        
        Args:
            proc: psutil Process object
            
        Returns:
            Dictionary with process information or None if collection fails
        """
        try:
            # Validate PID
            if not proc.pid or proc.pid <= 0:
                return None
                
            # Basic process info
            proc_info = proc.as_dict(attrs=[
                'pid', 'name', 'ppid', 'status', 'create_time', 'num_threads',
                'nice', 'username', 'exe', 'cmdline'
            ])
            
            # Validate PID again after as_dict
            if not proc_info.get('pid') or proc_info['pid'] <= 0:
                return None
                
            # CPU and memory info
            try:
                proc_info['cpu_percent'] = proc.cpu_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                proc_info['cpu_percent'] = 0.0
            
            try:
                memory_info = proc.memory_info()
                proc_info['memory_rss'] = memory_info.rss
                proc_info['memory_vms'] = memory_info.vms
                proc_info['memory_percent'] = proc.memory_percent()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                proc_info['memory_rss'] = 0
                proc_info['memory_vms'] = 0
                proc_info['memory_percent'] = 0.0
            
            # Platform-specific information
            proc_info.update(self.get_platform_specific_info(proc))
            
            # Check if process should be filtered out
            if self.should_filter_process(proc_info.get('name', '')):
                return None
                
            # Clean up None values and ensure required fields
            proc_info = {k: v for k, v in proc_info.items() if v is not None}
            
            # Final validation
            if not proc_info.get('pid') or proc_info['pid'] <= 0:
                return None
                
            return proc_info
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return None
        except Exception as e:
            self.logger.warning(f"Error collecting info for process {proc.pid}: {e}")
            return None
    
    def should_filter_process(self, process_name: str) -> bool:
        """
        Check if a process should be filtered out based on its name
        
        Args:
            process_name: Name of the process to check
            
        Returns:
            True if process should be filtered out, False otherwise
        """
        if not process_name:
            return False
            
        # Convert to lowercase for case-insensitive comparison
        process_name_lower = process_name.lower()
        
        # Check if process name contains any filtered terms
        for filtered_term in self.filtered_processes:
            if filtered_term in process_name_lower:
                return True
                
        return False
    
    def get_platform_specific_info(self, proc: psutil.Process) -> Dict[str, Any]:
        """
        Get platform-specific process information
        
        Args:
            proc: psutil Process object
            
        Returns:
            Dictionary with platform-specific information
        """
        platform_info = {}
        
        try:
            if psutil.WINDOWS:
                # Windows-specific information
                try:
                    platform_info['working_set'] = proc.memory_info().working_set
                except:
                    platform_info['working_set'] = None
                
                try:
                    platform_info['private_bytes'] = proc.memory_info().private
                except:
                    platform_info['private_bytes'] = None
                    
            elif psutil.LINUX:
                # Linux-specific information
                try:
                    with open(f"/proc/{proc.pid}/stat", 'r') as f:
                        stat_data = f.read().split()
                        if len(stat_data) > 22:
                            platform_info['nice'] = int(stat_data[18])
                except:
                    pass
                    
            elif psutil.MACOS:
                # macOS-specific information
                try:
                    platform_info['real_memory'] = proc.memory_info().rss
                except:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Could not get platform-specific info: {e}")
        
        return platform_info
    
    def get_system_metrics(self) -> Optional[Dict[str, Any]]:
        """
        Collect system-level metrics
        
        Returns:
            Dictionary with system metrics or None if collection fails
        """
        try:
            metrics = {}
            
            # CPU information
            try:
                cpu_percent = psutil.cpu_percent(interval=1)
                metrics['system_cpu_percent'] = cpu_percent
                
                cpu_count = psutil.cpu_count()
                metrics['cpu_count'] = cpu_count
                
                if hasattr(psutil, 'cpu_freq'):
                    cpu_freq = psutil.cpu_freq()
                    if cpu_freq:
                        metrics['cpu_freq_current'] = cpu_freq.current
                        metrics['cpu_freq_min'] = cpu_freq.min
                        metrics['cpu_freq_max'] = cpu_freq.max
            except Exception as e:
                self.logger.debug(f"Could not collect CPU metrics: {e}")
            
            # Memory information
            try:
                memory = psutil.virtual_memory()
                metrics['system_memory_percent'] = memory.percent
                metrics['memory_total'] = memory.total
                metrics['memory_available'] = memory.available
                metrics['memory_used'] = memory.used
                metrics['memory_free'] = memory.free
            except Exception as e:
                self.logger.debug(f"Could not collect memory metrics: {e}")
            
            # Disk information
            try:
                disk_usage = {}
                for partition in psutil.disk_partitions():
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_usage[partition.device] = {
                            'mountpoint': partition.mountpoint,
                            'total': usage.total,
                            'used': usage.used,
                            'free': usage.free,
                            'percent': usage.percent
                        }
                    except PermissionError:
                        continue
                metrics['disk_usage'] = disk_usage
            except Exception as e:
                self.logger.debug(f"Could not collect disk metrics: {e}")
            
            # Network information
            try:
                network_io = psutil.net_io_counters()
                metrics['network_io'] = {
                    'bytes_sent': network_io.bytes_sent,
                    'bytes_recv': network_io.bytes_recv,
                    'packets_sent': network_io.packets_sent,
                    'packets_recv': network_io.packets_recv
                }
            except Exception as e:
                self.logger.debug(f"Could not collect network metrics: {e}")
            
            return metrics if metrics else None
            
        except Exception as e:
            self.logger.warning(f"Error collecting system metrics: {e}")
            return None
    
    def get_process_tree(self) -> Dict[str, Any]:
        """
        Get hierarchical process tree structure
        
        Returns:
            Dictionary with process tree information
        """
        try:
            processes = self.collect_all_processes()
            
            # Create process lookup dictionary
            process_dict = {p['pid']: p for p in processes}
            
            # Build tree structure
            root_processes = []
            for process in processes:
                if not process.get('ppid') or process['ppid'] not in process_dict:
                    # This is a root process
                    tree_node = self.build_tree_node(process, process_dict)
                    root_processes.append(tree_node)
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_processes': len(processes),
                'root_processes': root_processes
            }
            
        except Exception as e:
            self.logger.error(f"Error building process tree: {e}")
            return {}
    
    def build_tree_node(self, process: Dict[str, Any], process_dict: Dict[int, Dict]) -> Dict[str, Any]:
        """
        Build a tree node with children
        
        Args:
            process: Process information dictionary
            process_dict: Dictionary of all processes by PID
            
        Returns:
            Tree node dictionary
        """
        node = {
            'process': process,
            'children': []
        }
        
        # Find child processes
        children = [p for p in process_dict.values() if p.get('ppid') == process['pid']]
        for child in children:
            child_node = self.build_tree_node(child, process_dict)
            node['children'].append(child_node)
        
        return node
    
    def get_top_processes(self, metric: str = 'cpu', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top processes by specified metric
        
        Args:
            metric: Metric to sort by ('cpu' or 'memory')
            limit: Number of processes to return
            
        Returns:
            List of top processes
        """
        try:
            processes = self.collect_all_processes()
            
            if metric == 'cpu':
                processes.sort(key=lambda x: x.get('cpu_percent', 0), reverse=True)
            elif metric == 'memory':
                processes.sort(key=lambda x: x.get('memory_rss', 0), reverse=True)
            else:
                self.logger.warning(f"Unknown metric: {metric}")
                return []
            
            return processes[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting top processes: {e}")
            return []
    
    def get_process_by_pid(self, pid: int) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific process by PID
        
        Args:
            pid: Process ID
            
        Returns:
            Process information dictionary or None if not found
        """
        try:
            proc = psutil.Process(pid)
            return self.collect_process_info(proc)
        except psutil.NoSuchProcess:
            return None
        except Exception as e:
            self.logger.error(f"Error getting process {pid}: {e}")
            return None
    
    def get_process_count(self) -> int:
        """
        Get total number of running processes
        
        Returns:
            Number of processes
        """
        try:
            return len(psutil.pids())
        except Exception as e:
            self.logger.error(f"Error getting process count: {e}")
            return 0
    
    def is_collection_due(self, interval: int = 60) -> bool:
        """
        Check if it's time to collect process information
        
        Args:
            interval: Collection interval in seconds
            
        Returns:
            True if collection is due, False otherwise
        """
        if self.last_collection_time is None:
            return True
        
        return (time.time() - self.last_collection_time) >= interval
