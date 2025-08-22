#!/usr/bin/env python3
"""
Process Monitor Agent
Main entry point for the process monitoring system

This agent collects process information from the local system and sends it to the Django backend.
It can be run as a standalone script or compiled to an executable.
"""

import sys
import os
import time
import logging
import signal
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

from process_collector import ProcessCollector
from api_client import APIClient
from config import AgentConfig
from utils import setup_logging, get_system_info


class ProcessMonitorAgent:
    """
    Main agent class that orchestrates process monitoring and data submission
    """
    
    def __init__(self):
        self.config = AgentConfig()
        self.process_collector = ProcessCollector(config=self.config)
        self.api_client = APIClient(
            base_url=self.config.backend_url,
            api_key=self.config.api_key
        )
        self.running = False
        self.collection_interval = self.config.collection_interval
        
        # Setup logging
        setup_logging(
            log_level=self.config.log_level,
            log_file=self.config.log_file
        )
        self.logger = logging.getLogger(__name__)
        
        # Setup signal handlers
        self.setup_signal_handlers()
        
        # Get system information
        self.system_info = get_system_info()
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Windows-specific signals
        if hasattr(signal, 'SIGBREAK'):
            signal.signal(signal.SIGBREAK, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop()
    
    def start(self):
        """Start the process monitoring agent"""
        self.logger.info("Starting Process Monitor Agent...")
        self.logger.info(f"System: {self.system_info['platform']} {self.system_info['architecture']}")
        self.logger.info(f"Hostname: {self.system_info['hostname']}")
        self.logger.info(f"Backend URL: {self.config.backend_url}")
        self.logger.info(f"Collection interval: {self.collection_interval} seconds")
        
        self.running = True
        
        try:
            while self.running:
                self.collect_andSubmit()
                time.sleep(self.collection_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise
        finally:
            self.stop()
    
    def collect_andSubmit(self):
        """Collect process data and submit to backend"""
        try:
            # Collect process information
            self.logger.debug("Collecting process information...")
            process_data = self.process_collector.collect_all_processes()
            
            if not process_data:
                self.logger.warning("No process data collected")
                return
            
            # Prepare data for submission
            submission_data = self.prepare_submission_data(process_data)
            
            # Submit to backend
            self.logger.debug(f"Submitting {len(process_data)} processes to backend...")
            response = self.api_client.submit_process_data(submission_data)
            
            if response.get('success'):
                self.logger.info(f"Successfully submitted {len(process_data)} processes")
            else:
                self.logger.error(f"Failed to submit data: {response.get('error', 'Unknown error')}")
                
        except Exception as e:
            self.logger.error(f"Error in collect_andSubmit: {e}")
    
    def prepare_submission_data(self, process_data):
        """Prepare process data for API submission"""
        submission_data = {
            'hostname': self.system_info['hostname'],
            'platform': self.system_info['platform'],
            'architecture': self.system_info['architecture'],
            'cpu_count': self.system_info['cpu_count'],
            'total_memory': self.system_info['total_memory'],
            'os_info': self.system_info['os_info'],
            'ip_address': self.system_info['ip_address'],
            'processes': process_data
        }
        
        # Add system metrics if available
        try:
            system_metrics = self.process_collector.get_system_metrics()
            if system_metrics:
                submission_data.update(system_metrics)
        except Exception as e:
            self.logger.warning(f"Could not collect system metrics: {e}")
        
        return submission_data
    
    def stop(self):
        """Stop the agent"""
        self.logger.info("Stopping Process Monitor Agent...")
        self.running = False
        self.logger.info("Agent stopped")


def main():
    """Main entry point"""
    try:
        agent = ProcessMonitorAgent()
        agent.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
