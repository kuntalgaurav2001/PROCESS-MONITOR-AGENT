"""
API Client Module
Handles communication with the Django backend
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from requests.exceptions import RequestException


class APIClient:
    """Client for communicating with the Django backend API"""
    
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # Setup session headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'X-API-Key': api_key,
            'User-Agent': 'ProcessMonitorAgent/1.0'
        })
    
    def submit_process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Submit process data to the backend"""
        try:
            url = f"{self.base_url}/submit/"
            response = self.session.post(url, json=data, timeout=self.timeout)
            
            if response.status_code == 201:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}
                
        except RequestException as e:
            self.logger.error(f"API request failed: {e}")
            return {'success': False, 'error': str(e)}
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            return {'success': False, 'error': str(e)}
    
    def test_connection(self) -> bool:
        """Test connection to the backend"""
        try:
            url = f"{self.base_url}/hosts/"
            response = self.session.get(url, timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def close(self):
        """Close the session"""
        self.session.close()
