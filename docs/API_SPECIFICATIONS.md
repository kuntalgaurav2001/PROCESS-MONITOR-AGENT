# Process Monitoring System - API Specifications

## Overview

The Process Monitoring System provides a RESTful API for collecting, storing, and retrieving process monitoring data. The API follows REST principles and uses JSON for data exchange.

## Base URL

```
Development: http://localhost:8000/api/v1/
Production: https://your-domain.com/api/v1/
```

## Authentication

### API Key Authentication
All agent endpoints require authentication using an API key in the request header:

```
X-API-Key: your-secure-api-key-here
```

### Public Endpoints
Frontend endpoints are publicly accessible for read operations.

## API Endpoints

### 1. Process Data Submission

#### Submit Process Data
**Endpoint**: `POST /submit/`

**Description**: Submit process monitoring data from an agent

**Authentication**: Required (API Key)

**Request Headers**:
```
Content-Type: application/json
X-API-Key: your-secure-api-key
```

**Request Body**:
```json
{
  "hostname": "workstation-01",
  "ip_address": "192.168.1.100",
  "os_info": "Windows 10 Pro",
  "platform": "Windows",
  "architecture": "x86_64",
  "cpu_count": 8,
  "total_memory": 17179869184,
  "processes": [
    {
      "pid": 1234,
      "ppid": 1,
      "name": "explorer.exe",
      "exe": "C:\\Windows\\explorer.exe",
      "cmdline": "explorer.exe",
      "status": "running",
      "username": "user",
      "cpu_percent": 2.5,
      "memory_rss": 52428800,
      "memory_vms": 104857600,
      "create_time": 1640995200.0,
      "num_threads": 15,
      "nice": 0
    }
  ],
  "system_metrics": {
    "cpu_count": 8,
    "cpu_freq_current": 2400.0,
    "cpu_freq_min": 800.0,
    "cpu_freq_max": 3200.0,
    "memory_total": 17179869184,
    "memory_available": 8589934592,
    "memory_used": 8589934592,
    "memory_free": 8589934592,
    "memory_percent": 50.0,
    "disk_usage": {
      "C:": {
        "total": 500000000000,
        "used": 250000000000,
        "free": 250000000000,
        "percent": 50.0
      }
    },
    "network_io": {
      "bytes_sent": 1048576,
      "bytes_recv": 2097152,
      "packets_sent": 1000,
      "packets_recv": 2000
    }
  }
}
```

**Response**:
```json
{
  "id": "uuid-string",
  "hostname": "workstation-01",
  "timestamp": "2025-08-21T10:00:00Z",
  "processes_count": 150,
  "status": "success"
}
```

**Status Codes**:
- `201 Created`: Data successfully submitted
- `400 Bad Request`: Invalid data format
- `401 Unauthorized`: Invalid or missing API key
- `500 Internal Server Error`: Server error

### 2. Host Management

#### Get Hosts Summary
**Endpoint**: `GET /hosts/summary/`

**Description**: Get summary information about all monitored hosts

**Authentication**: Public (Read-only)

**Query Parameters**:
- `platform` (optional): Filter by platform (Windows, macOS, Linux)
- `active` (optional): Filter by active status (true/false)
- `hostname` (optional): Search by hostname

**Response**:
```json
[
  {
    "id": "uuid-string",
    "hostname": "workstation-01",
    "platform": "Windows",
    "architecture": "x86_64",
    "cpu_count": 8,
    "total_memory_gb": 16.0,
    "is_active": true,
    "last_seen": "2025-08-21T10:00:00Z",
    "uptime_hours": 24.5,
    "latest_snapshot": {
      "timestamp": "2025-08-21T10:00:00Z",
      "total_processes": 150,
      "total_cpu_percent": 25.5,
      "total_memory_mb": 8192.0
    },
    "process_count": 150
  }
]
```

#### Get Host Details
**Endpoint**: `GET /hosts/{host_id}/`

**Description**: Get detailed information about a specific host

**Authentication**: Public (Read-only)

**Response**:
```json
{
  "id": "uuid-string",
  "hostname": "workstation-01",
  "ip_address": "192.168.1.100",
  "os_info": "Windows 10 Pro",
  "platform": "Windows",
  "architecture": "x86_64",
  "cpu_count": 8,
  "total_memory": 17179869184,
  "total_memory_gb": 16.0,
  "is_active": true,
  "first_seen": "2025-08-21T09:00:00Z",
  "last_seen": "2025-08-21T10:00:00Z",
  "uptime_hours": 24.5,
  "created_at": "2025-08-21T09:00:00Z",
  "updated_at": "2025-08-21T10:00:00Z"
}
```

### 3. Process Snapshots

#### Get Latest Snapshots
**Endpoint**: `GET /snapshots/latest/`

**Description**: Get the latest process snapshot for each host

**Authentication**: Public (Read-only)

**Query Parameters**:
- `hostname` (optional): Filter by hostname
- `limit` (optional): Maximum number of snapshots (default: 100)

**Response**:
```json
[
  {
    "id": "uuid-string",
    "host": {
      "id": "host-uuid",
      "hostname": "workstation-01",
      "platform": "Windows"
    },
    "timestamp": "2025-08-21T10:00:00Z",
    "total_processes": 150,
    "total_cpu_percent": 25.5,
    "total_memory_mb": 8192.0,
    "system_cpu_percent": 15.2,
    "system_memory_percent": 47.8,
    "created_at": "2025-08-21T10:00:00Z"
  }
]
```

#### Get Snapshot Details
**Endpoint**: `GET /snapshots/{snapshot_id}/`

**Description**: Get detailed information about a specific snapshot

**Authentication**: Public (Read-only)

**Response**:
```json
{
  "id": "uuid-string",
  "host": {
    "id": "host-uuid",
    "hostname": "workstation-01"
  },
  "timestamp": "2025-08-21T10:00:00Z",
  "total_processes": 150,
  "total_cpu_percent": 25.5,
  "total_memory_mb": 8192.0,
  "system_cpu_percent": 15.2,
  "system_memory_percent": 47.8,
  "processes": [
    {
      "id": "process-uuid",
      "pid": 1234,
      "ppid": 1,
      "name": "explorer.exe",
      "status": "running",
      "cpu_percent": 2.5,
      "memory_rss_mb": 50.0,
      "memory_vms_mb": 100.0,
      "username": "user",
      "create_time": 1640995200.0,
      "num_threads": 15
    }
  ],
  "created_at": "2025-08-21T10:00:00Z"
}
```

#### Get Process Tree
**Endpoint**: `GET /snapshots/{snapshot_id}/tree/`

**Description**: Get hierarchical process tree for a snapshot

**Authentication**: Public (Read-only)

**Response**:
```json
[
  {
    "process": {
      "id": "process-uuid",
      "pid": 1,
      "name": "systemd",
      "status": "running",
      "cpu_percent": 0.1,
      "memory_rss_mb": 5.0
    },
    "children": [
      {
        "process": {
          "id": "child-uuid",
          "pid": 1234,
          "ppid": 1,
          "name": "explorer.exe",
          "status": "running",
          "cpu_percent": 2.5,
          "memory_rss_mb": 50.0
        },
        "children": []
      }
    ]
  }
]
```

### 4. Process Management

#### Get Processes
**Endpoint**: `GET /processes/`

**Description**: Get list of processes with filtering and pagination

**Authentication**: Public (Read-only)

**Query Parameters**:
- `snapshot` (optional): Filter by snapshot ID
- `hostname` (optional): Filter by hostname
- `name` (optional): Search by process name
- `status` (optional): Filter by process status
- `username` (optional): Filter by username
- `min_cpu` (optional): Minimum CPU percentage
- `max_cpu` (optional): Maximum CPU percentage
- `min_memory` (optional): Minimum memory usage (bytes)
- `max_memory` (optional): Maximum memory usage (bytes)
- `limit` (optional): Maximum results per page (default: 100)
- `offset` (optional): Number of results to skip

**Response**:
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/processes/?limit=100&offset=100",
  "previous": null,
  "results": [
    {
      "id": "process-uuid",
      "snapshot": "snapshot-uuid",
      "pid": 1234,
      "ppid": 1,
      "name": "explorer.exe",
      "exe": "C:\\Windows\\explorer.exe",
      "cmdline": "explorer.exe",
      "status": "running",
      "cpu_percent": 2.5,
      "memory_rss": 52428800,
      "memory_rss_mb": 50.0,
      "memory_vms": 104857600,
      "memory_vms_mb": 100.0,
      "memory_percent": 0.3,
      "create_time": 1640995200.0,
      "num_threads": 15,
      "nice": 0,
      "username": "user",
      "parent_process_name": "systemd",
      "child_processes_count": 5,
      "uptime_seconds": 86400,
      "created_at": "2025-08-21T10:00:00Z"
    }
  ]
}
```

#### Search Processes
**Endpoint**: `POST /processes/search/`

**Description**: Advanced process search with multiple criteria

**Authentication**: Public (Read-only)

**Request Body**:
```json
{
  "hostname": "workstation-01",
  "process_name": "explorer",
  "status": "running",
  "username": "user",
  "min_cpu": 1.0,
  "max_cpu": 10.0,
  "min_memory": 1000000,
  "max_memory": 100000000
}
```

**Response**: Same format as GET /processes/

#### Get Top CPU Processes
**Endpoint**: `GET /processes/top-cpu/`

**Description**: Get processes with highest CPU usage

**Authentication**: Public (Read-only)

**Query Parameters**:
- `limit` (optional): Number of processes (default: 10)
- `hostname` (optional): Filter by hostname

**Response**:
```json
[
  {
    "id": "process-uuid",
    "name": "chrome.exe",
    "pid": 5678,
    "cpu_percent": 15.2,
    "memory_rss_mb": 200.0,
    "username": "user"
  }
]
```

#### Get Top Memory Processes
**Endpoint**: `GET /processes/top-memory/`

**Description**: Get processes with highest memory usage

**Authentication**: Public (Read-only)

**Query Parameters**:
- `limit` (optional): Number of processes (default: 10)
- `hostname` (optional): Filter by hostname

**Response**: Same format as top-cpu endpoint

### 5. System Metrics

#### Get Latest System Metrics
**Endpoint**: `GET /system-metrics/latest/`

**Description**: Get latest system metrics for all hosts

**Authentication**: Public (Read-only)

**Query Parameters**:
- `hostname` (optional): Filter by hostname
- `limit` (optional): Maximum number of metrics (default: 100)

**Response**:
```json
[
  {
    "id": "uuid-string",
    "host": {
      "id": "host-uuid",
      "hostname": "workstation-01"
    },
    "timestamp": "2025-08-21T10:00:00Z",
    "cpu_count": 8,
    "cpu_freq_current": 2400.0,
    "cpu_freq_min": 800.0,
    "cpu_freq_max": 3200.0,
    "memory_total": 17179869184,
    "memory_total_gb": 16.0,
    "memory_available": 8589934592,
    "memory_available_gb": 8.0,
    "memory_used": 8589934592,
    "memory_free": 8589934592,
    "memory_percent": 50.0,
    "disk_usage": {
      "C:": {
        "total": 500000000000,
        "used": 250000000000,
        "free": 250000000000,
        "percent": 50.0
      }
    },
    "network_io": {
      "bytes_sent": 1048576,
      "bytes_recv": 2097152,
      "packets_sent": 1000,
      "packets_recv": 2000
    },
    "created_at": "2025-08-21T10:00:00Z"
  }
]
```

## Error Handling

### Error Response Format
```json
{
  "error": "Error message description",
  "detail": "Additional error details",
  "code": "ERROR_CODE",
  "timestamp": "2025-08-21T10:00:00Z"
}
```

### Common Error Codes
- `INVALID_API_KEY`: Invalid or missing API key
- `INVALID_DATA`: Request data validation failed
- `HOST_NOT_FOUND`: Specified host not found
- `SNAPSHOT_NOT_FOUND`: Specified snapshot not found
- `PROCESS_NOT_FOUND`: Specified process not found
- `RATE_LIMIT_EXCEEDED`: Too many requests
- `INTERNAL_ERROR`: Server internal error

### HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Rate Limiting

### Limits
- **Agent endpoints**: 100 requests per minute
- **Public endpoints**: 1000 requests per minute
- **Admin endpoints**: 50 requests per minute

### Headers
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995260
```

## Pagination

### Pagination Parameters
- `limit`: Number of results per page (default: 100, max: 1000)
- `offset`: Number of results to skip

### Pagination Response
```json
{
  "count": 1500,
  "next": "http://localhost:8000/api/v1/processes/?limit=100&offset=100",
  "previous": null,
  "results": [...]
}
```

## Data Types

### Timestamps
All timestamps are in ISO 8601 format with UTC timezone:
```
2025-08-21T10:00:00Z
```

### Numeric Values
- **CPU percentages**: Float values (0.0 - 100.0)
- **Memory values**: Bytes (converted to MB/GB in responses)
- **Process IDs**: Positive integers
- **Timestamps**: Unix timestamp (seconds since epoch)

### Enums
- **Process Status**: `running`, `sleeping`, `stopped`, `zombie`, `dead`
- **Platform**: `Windows`, `macOS`, `Linux`
- **Architecture**: `x86_64`, `ARM64`, `i386`

## WebSocket Support (Future)

### Real-time Updates
```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/processes/');

// Listen for updates
ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Process update:', data);
};

// Subscribe to specific host
ws.send(JSON.stringify({
  action: 'subscribe',
  hostname: 'workstation-01'
}));
```

## SDK Examples

### Python Client
```python
import requests

class ProcessMonitorClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url
        self.headers = {}
        if api_key:
            self.headers['X-API-Key'] = api_key
    
    def get_hosts(self):
        response = requests.get(f"{self.base_url}/hosts/summary/")
        return response.json()
    
    def submit_data(self, data):
        response = requests.post(
            f"{self.base_url}/submit/",
            json=data,
            headers=self.headers
        )
        return response.json()
```

### JavaScript Client
```javascript
class ProcessMonitorClient {
  constructor(baseUrl, apiKey = null) {
    this.baseUrl = baseUrl;
    this.headers = {};
    if (apiKey) {
      this.headers['X-API-Key'] = apiKey;
    }
  }
  
  async getHosts() {
    const response = await fetch(`${this.baseUrl}/hosts/summary/`);
    return response.json();
  }
  
  async submitData(data) {
    const response = await fetch(`${this.baseUrl}/submit/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...this.headers
      },
      body: JSON.stringify(data)
    });
    return response.json();
  }
}
```

## Testing

### Test Endpoints
- **Health Check**: `GET /health/`
- **API Status**: `GET /status/`
- **Test Connection**: `POST /test-connection/`

### Test Data
Use the provided test scripts to populate the system with sample data:
```bash
python create_sample_data.py
```

## Security Considerations

### API Key Management
- Generate strong, unique API keys
- Rotate keys regularly
- Use environment variables for storage
- Never commit keys to version control

### Network Security
- Use HTTPS in production
- Implement firewall rules
- Consider VPN for private networks
- Monitor API access logs

### Data Privacy
- Enable process filtering
- Implement data retention policies
- Audit data access
- Consider data encryption

## Performance Guidelines

### Best Practices
1. **Use pagination** for large datasets
2. **Implement caching** for frequently accessed data
3. **Batch requests** when possible
4. **Monitor response times** and optimize slow queries
5. **Use appropriate HTTP methods** (GET for read, POST for write)

### Optimization Tips
- Request only needed fields
- Use appropriate time ranges for historical data
- Implement client-side caching
- Monitor API usage and adjust limits

---

**Note**: This API specification is current as of version 1.0. For the latest updates and additional endpoints, refer to the system documentation or contact the development team.
