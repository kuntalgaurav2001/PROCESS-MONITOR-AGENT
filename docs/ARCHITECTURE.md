# Process Monitoring System - Architecture Overview

## System Overview

The Process Monitoring System is a distributed application designed to collect, store, and visualize real-time process information from multiple hosts. The system consists of three main components:

1. **Agent** - Cross-platform process monitoring executable
2. **Backend** - Django REST API server with SQLite database
3. **Frontend** - Web-based dashboard for process visualization

## Architecture Diagram

```
┌─────────────────┐    HTTP/REST    ┌─────────────────┐    WebSocket/HTTP    ┌─────────────────┐
│                 │ ◄──────────────► │                 │ ◄──────────────────► │                 │
│   Agent(s)      │                 │   Django        │                      │   Web Frontend  │
│   (Executable)  │                 │   Backend       │                      │   (Browser)     │
│                 │                 │                 │                      │                 │
└─────────────────┘                 └─────────────────┘                      └─────────────────┘
         │                                   │                                        │
         │                                   │                                        │
         ▼                                   ▼                                        ▼
┌─────────────────┐                 ┌─────────────────┐                      ┌─────────────────┐
│                 │                 │                 │                      │                 │
│   System        │                 │   SQLite        │                      │   Process Tree  │
│   Processes     │                 │   Database      │                      │   Visualization │
│                 │                 │                 │                      │                 │
└─────────────────┘                 └─────────────────┘                      └─────────────────┘
```

## Component Details

### 1. Agent Component

#### Purpose
- Collects real-time process information from the host system
- Monitors system resources (CPU, memory, disk, network)
- Sends data to the backend via REST API
- Runs as a standalone executable (no installation required)

#### Technology Stack
- **Language**: Python 3.8+
- **Core Libraries**: psutil, requests, python-dotenv
- **Packaging**: PyInstaller for cross-platform compilation
- **Communication**: HTTP REST API calls

#### Key Features
- **Cross-Platform**: Windows, macOS, Linux support
- **Privacy-Focused**: Configurable process filtering
- **Resource Efficient**: Minimal memory and CPU footprint
- **Configurable**: Environment-based configuration
- **Robust**: Error handling and retry mechanisms

#### Data Collection
```python
# Process Information
- Process ID (PID)
- Parent Process ID (PPID)
- Process Name
- Executable Path
- Command Line Arguments
- Username
- Status (running, sleeping, stopped, zombie)
- Creation Time
- CPU Usage Percentage
- Memory Usage (RSS, VMS)
- Thread Count
- Nice Value
- Working Directory

# System Information
- Hostname
- Platform (Windows, macOS, Linux)
- Architecture (x86_64, ARM64)
- CPU Count
- Total Memory
- Operating System Version
```

### 2. Backend Component

#### Purpose
- Receives and stores process data from agents
- Provides REST API endpoints for data retrieval
- Manages host identification and authentication
- Handles data persistence and relationships

#### Technology Stack
- **Framework**: Django 5.2+
- **API**: Django REST Framework
- **Database**: SQLite (configurable for production)
- **Authentication**: API Key-based
- **CORS**: django-cors-headers for frontend access

#### Key Features
- **RESTful API**: Standard HTTP methods and status codes
- **Authentication**: Simple API key validation
- **Data Modeling**: Comprehensive process and system data models
- **Caching**: Built-in Django caching support
- **Admin Interface**: Django admin for data management

#### Database Schema

##### Host Model
```python
class Host(models.Model):
    hostname = models.CharField(max_length=255, unique=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    os_info = models.CharField(max_length=255)
    platform = models.CharField(max_length=50)
    architecture = models.CharField(max_length=50)
    cpu_count = models.IntegerField()
    total_memory = models.BigIntegerField()
    is_active = models.BooleanField(default=True)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
```

##### ProcessSnapshot Model
```python
class ProcessSnapshot(models.Model):
    host = models.ForeignKey(Host, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    total_processes = models.IntegerField()
    total_cpu_percent = models.FloatField()
    total_memory_mb = models.FloatField()
    system_cpu_percent = models.FloatField()
    system_memory_percent = models.FloatField()
```

##### Process Model
```python
class Process(models.Model):
    snapshot = models.ForeignKey(ProcessSnapshot, on_delete=models.CASCADE)
    pid = models.IntegerField()
    ppid = models.IntegerField(null=True)
    name = models.CharField(max_length=255)
    exe = models.CharField(max_length=500, null=True)
    cmdline = models.TextField(null=True)
    status = models.CharField(max_length=50)
    username = models.CharField(max_length=100)
    cpu_percent = models.FloatField()
    memory_rss = models.BigIntegerField()
    memory_vms = models.BigIntegerField()
    create_time = models.FloatField()
    num_threads = models.IntegerField()
```

### 3. Frontend Component

#### Purpose
- Provides web-based interface for process monitoring
- Displays process hierarchy and relationships
- Shows real-time system metrics and analytics
- Enables process search and filtering

#### Technology Stack
- **HTML5**: Semantic markup and accessibility
- **CSS3**: Bootstrap 5.3 for responsive design
- **JavaScript**: Vanilla JS with ES6+ features
- **Charts**: Chart.js for data visualization
- **Icons**: Font Awesome for UI elements

#### Key Features
- **Responsive Design**: Mobile and desktop compatible
- **Interactive Process Tree**: Expandable/collapsible process hierarchy
- **Real-time Updates**: Automatic data refresh
- **Search & Filter**: Process name and status filtering
- **Analytics Dashboard**: System metrics and process statistics

#### UI Components
```html
<!-- Navigation -->
- Dashboard: Overview and summary
- Processes: List view with search/filter
- Process Tree: Hierarchical visualization
- Hosts: Host management and status
- Analytics: Charts and metrics

<!-- Process Tree -->
- Expandable nodes for parent-child relationships
- Process details on hover/click
- Status indicators and resource usage
- Search and navigation controls
```

## Data Flow

### 1. Data Collection Flow
```
Agent Startup → System Scan → Process Collection → Data Processing → API Submission → Database Storage
```

### 2. Data Retrieval Flow
```
Frontend Request → API Endpoint → Database Query → Data Serialization → JSON Response → UI Rendering
```

### 3. Real-time Updates Flow
```
Agent Collection → Database Update → Frontend Polling → Data Refresh → UI Update
```

## Security Model

### Authentication
- **API Key Authentication**: Simple but effective for agent-backend communication
- **CORS Protection**: Configurable origins for frontend access
- **Input Validation**: Comprehensive data validation and sanitization

### Privacy Features
- **Process Filtering**: Configurable exclusion of sensitive applications
- **Data Retention**: Configurable data retention policies
- **Access Control**: Environment-based configuration management

### Network Security
- **HTTPS Support**: TLS encryption for production deployments
- **Firewall Considerations**: Port 8000 for backend access
- **Network Isolation**: Optional VPN or private network deployment

## Performance Characteristics

### Scalability
- **Horizontal Scaling**: Multiple agents per backend
- **Database Optimization**: Indexed queries and efficient relationships
- **Caching Strategy**: Django's built-in caching framework

### Resource Usage
- **Agent Memory**: ~50-100MB per agent instance
- **Backend Memory**: ~200-500MB for Django server
- **Database Size**: ~1-10MB per host per day (depending on process count)

### Performance Metrics
- **Data Collection**: 1000+ processes in <5 seconds
- **API Response**: <100ms for standard queries
- **Frontend Rendering**: <2 seconds for process tree display

## Deployment Models

### 1. Development Environment
```
Single Host: Agent + Backend + Frontend
Database: SQLite
Server: Django development server
```

### 2. Production Environment
```
Multiple Hosts: Distributed agents
Backend: Gunicorn/uWSGI + Nginx
Database: PostgreSQL/MySQL
Monitoring: Health checks and logging
```

### 3. Containerized Deployment
```
Docker containers for each component
Docker Compose for orchestration
Volume mounts for data persistence
Environment-based configuration
```

## Monitoring and Observability

### Logging
- **Agent Logs**: Process collection and API communication
- **Backend Logs**: Django application and database operations
- **Access Logs**: API endpoint usage and performance

### Metrics
- **System Metrics**: CPU, memory, disk usage
- **Application Metrics**: API response times, error rates
- **Business Metrics**: Process counts, host status

### Health Checks
- **Agent Health**: Process collection status
- **Backend Health**: Database connectivity and API responsiveness
- **Frontend Health**: Static file serving and JavaScript execution

## Future Enhancements

### Planned Features
1. **Real-time Updates**: WebSocket support for live data
2. **Advanced Analytics**: Machine learning for process behavior
3. **Alerting System**: Threshold-based notifications
4. **Multi-tenant Support**: Organization and user management
5. **Mobile Application**: Native mobile app for monitoring

### Technical Improvements
1. **Microservices Architecture**: Service decomposition
2. **Event Streaming**: Apache Kafka for real-time data
3. **GraphQL API**: Flexible data querying
4. **Container Orchestration**: Kubernetes deployment
5. **Cloud Integration**: AWS/Azure/GCP deployment options

## Assumptions and Limitations

### Assumptions
1. **Network Connectivity**: Agents can reach backend via HTTP
2. **System Access**: Agents have sufficient permissions to read process data
3. **Resource Availability**: Adequate memory and CPU for monitoring
4. **Data Privacy**: Process filtering provides sufficient privacy protection

### Limitations
1. **Process Access**: Some system processes may be inaccessible
2. **Network Latency**: High latency may affect real-time updates
3. **Data Volume**: Large process counts may impact performance
4. **Platform Differences**: Process information varies by operating system

### Constraints
1. **Database Size**: SQLite limitations for very large datasets
2. **Concurrent Users**: Django development server limitations
3. **Real-time Updates**: Polling-based updates (not true real-time)
4. **Authentication**: Basic API key authentication (not enterprise-grade)

## Conclusion

The Process Monitoring System provides a robust, scalable solution for monitoring system processes across multiple platforms. The architecture balances simplicity with functionality, making it suitable for both development and production environments.

The system's modular design allows for easy customization and extension, while the comprehensive documentation ensures maintainability and ease of deployment.
