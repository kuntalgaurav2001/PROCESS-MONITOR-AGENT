"""
Configuration Module
Handles agent configuration and environment variables
"""

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any


class AgentConfig:
    """Configuration class for the process monitoring agent"""
    
    def __init__(self):
        # Load environment variables
        self.load_env()
        
        # Backend configuration
        self.backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000/api/v1')
        self.api_key = os.getenv('API_KEY', 'dev-api-key-change-in-production')
        
        # Collection settings
        self.collection_interval = int(os.getenv('COLLECTION_INTERVAL', '60'))
        self.max_processes = int(os.getenv('MAX_PROCESSES', '1000'))
        
        # Logging configuration
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.log_file = os.getenv('LOG_FILE', 'logs/agent.log')
        
        # Performance settings
        self.enable_system_metrics = os.getenv('ENABLE_SYSTEM_METRICS', 'true').lower() == 'true'
        self.enable_process_tree = os.getenv('ENABLE_PROCESS_TREE', 'true').lower() == 'true'
        
        # Privacy settings
        self.enable_process_filtering = os.getenv('ENABLE_PROCESS_FILTERING', 'true').lower() == 'true'
        self.filtered_process_names = os.getenv('FILTERED_PROCESS_NAMES', 'cursor,chrome,firefox,safari').split(',')
        
        # Network settings
        self.request_timeout = int(os.getenv('REQUEST_TIMEOUT', '30'))
        self.retry_attempts = int(os.getenv('RETRY_ATTEMPTS', '3'))
        self.retry_delay = int(os.getenv('RETRY_DELAY', '5'))
    
    def load_env(self):
        """Load environment variables from .env file"""
        env_file = Path(__file__).parent / 'env.agent'
        if env_file.exists():
            load_dotenv(env_file)
        
        # Also try to load from parent directory
        parent_env = Path(__file__).parent.parent / '.env'
        if parent_env.exists():
            load_dotenv(parent_env)
    
    def validate(self) -> bool:
        """Validate configuration settings"""
        errors = []
        
        if not self.backend_url:
            errors.append("BACKEND_URL is required")
        
        if not self.api_key:
            errors.append("API_KEY is required")
        
        if self.collection_interval < 10:
            errors.append("COLLECTION_INTERVAL must be at least 10 seconds")
        
        if self.max_processes < 100:
            errors.append("MAX_PROCESSES must be at least 100")
        
        if errors:
            for error in errors:
                logging.error(f"Configuration error: {error}")
            return False
        
        return True
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary"""
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'standard': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
                },
                'detailed': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': self.log_level,
                    'formatter': 'standard',
                    'stream': 'ext://sys.stdout'
                },
                'file': {
                    'class': 'logging.FileHandler',
                    'level': self.log_level,
                    'formatter': 'detailed',
                    'filename': self.log_file,
                    'mode': 'a'
                }
            },
            'loggers': {
                '': {
                    'handlers': ['console', 'file'],
                    'level': self.log_level,
                    'propagate': False
                }
            }
        }
