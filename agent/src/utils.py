"""
Utilities Module
Helper functions for the process monitoring agent
"""

import os
import sys
import platform
import socket
import logging.config
from pathlib import Path
from typing import Dict, Any


def setup_logging(log_level: str = 'INFO', log_file: str = 'logs/agent.log'):
    """Setup logging configuration"""
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file)
        ]
    )


def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    try:
        # Basic system info
        system_info = {
            'platform': platform.system(),
            'platform_version': platform.version(),
            'architecture': platform.machine(),
            'hostname': socket.gethostname(),
            'cpu_count': os.cpu_count(),
            'os_info': f"{platform.system()} {platform.release()}"
        }
        
        # Get IP address
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            system_info['ip_address'] = s.getsockname()[0]
            s.close()
        except:
            system_info['ip_address'] = '127.0.0.1'
        
        # Get total memory (platform-specific)
        try:
            if platform.system() == 'Windows':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulong = ctypes.c_ulong
                class MEMORYSTATUS(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", c_ulong),
                        ("dwMemoryLoad", c_ulong),
                        ("dwTotalPhys", ctypes.c_size_t),
                        ("dwAvailPhys", ctypes.c_size_t),
                        ("dwTotalPageFile", ctypes.c_size_t),
                        ("dwAvailPageFile", ctypes.c_size_t),
                        ("dwTotalVirtual", ctypes.c_size_t),
                        ("dwAvailVirtual", ctypes.c_size_t),
                    ]
                memoryStatus = MEMORYSTATUS()
                kernel32.GlobalMemoryStatus(ctypes.byref(memoryStatus))
                system_info['total_memory'] = memoryStatus.dwTotalPhys
            elif platform.system() == 'Linux':
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal:'):
                            system_info['total_memory'] = int(line.split()[1]) * 1024
                            break
            elif platform.system() == 'Darwin':  # macOS
                import subprocess
                result = subprocess.run(['sysctl', '-n', 'hw.memsize'], 
                                     capture_output=True, text=True)
                if result.returncode == 0:
                    system_info['total_memory'] = int(result.stdout.strip())
            else:
                system_info['total_memory'] = None
        except:
            system_info['total_memory'] = None
        
        return system_info
        
    except Exception as e:
        logging.error(f"Error getting system info: {e}")
        return {
            'platform': 'Unknown',
            'architecture': 'Unknown',
            'hostname': 'Unknown',
            'cpu_count': 1,
            'total_memory': None,
            'os_info': 'Unknown',
            'ip_address': '127.0.0.1'
        }


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format"""
    if bytes_value is None:
        return "Unknown"
    
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"


def format_percentage(value: float) -> str:
    """Format percentage value"""
    if value is None:
        return "0.0%"
    return f"{value:.1f}%"


def is_windows() -> bool:
    """Check if running on Windows"""
    return platform.system() == 'Windows'


def is_macos() -> bool:
    """Check if running on macOS"""
    return platform.system() == 'Darwin'


def is_linux() -> bool:
    """Check if running on Linux"""
    return platform.system() == 'Linux'


def get_executable_path() -> str:
    """Get the path to the current executable"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return sys.executable
    else:
        # Running as script
        return __file__


def create_pid_file(pid_file: str = 'agent.pid'):
    """Create PID file"""
    try:
        with open(pid_file, 'w') as f:
            f.write(str(os.getpid()))
        return True
    except Exception as e:
        logging.error(f"Could not create PID file: {e}")
        return False


def remove_pid_file(pid_file: str = 'agent.pid'):
    """Remove PID file"""
    try:
        if os.path.exists(pid_file):
            os.remove(pid_file)
        return True
    except Exception as e:
        logging.error(f"Could not remove PID file: {e}")
        return False


def check_pid_file(pid_file: str = 'agent.pid') -> bool:
    """Check if PID file exists and process is running"""
    try:
        if not os.path.exists(pid_file):
            return False
        
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if process is running
        os.kill(pid, 0)
        return True
        
    except (ValueError, OSError):
        # Process not running or invalid PID
        remove_pid_file(pid_file)
        return False


def get_agent_version() -> str:
    """Get agent version"""
    return "1.0.0"


def validate_backend_url(url: str) -> bool:
    """Validate backend URL format"""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return parsed.scheme in ('http', 'https') and parsed.netloc
    except:
        return False
