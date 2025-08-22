# Process Monitoring System - Build Instructions

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Backend (Django) Setup](#backend-django-setup)
3. [Agent Compilation](#agent-compilation)
4. [Frontend Setup](#frontend-setup)
5. [Configuration](#configuration)
6. [Running the System](#running-the-system)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python**: Python 3.8 or higher
- **Memory**: Minimum 4GB RAM, recommended 8GB+
- **Storage**: Minimum 2GB free space
- **Network**: Internet connection for package installation

### Required Software
- **Python 3.8+**: [Download from python.org](https://www.python.org/downloads/)
- **Git**: [Download from git-scm.com](https://git-scm.com/downloads)
- **Node.js** (optional, for frontend development): [Download from nodejs.org](https://nodejs.org/)

## Backend (Django) Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd process-monitor-system
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv backend/venv
backend\venv\Scripts\activate

# macOS/Linux
python3 -m venv backend/venv
source backend/venv/bin/activate
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp env.config.example env.config

# Edit env.config with your settings
# Key variables to configure:
# - SECRET_KEY: Generate a unique secret key
# - DEBUG: Set to False for production
# - API_KEY: Set a secure API key for agent authentication
# - ALLOWED_HOSTS: Add your server's IP/domain
```

### 5. Database Setup
```bash
# Create database migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic
```

### 6. Run Django Server
```bash
# Development server
python manage.py runserver 0.0.0.0:8000

# Production server (using gunicorn)
pip install gunicorn
gunicorn process_monitor.wsgi:application --bind 0.0.0.0:8000
```

## Agent Compilation

### 1. Setup Agent Environment
```bash
cd agent

# Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Install PyInstaller
```bash
pip install pyinstaller
```

### 3. Compile for Different Platforms

#### Windows (.exe)
```bash
# Basic compilation
pyinstaller --onefile --windowed src/main.py

# Advanced compilation with icon and metadata
pyinstaller --onefile --windowed \
    --icon=assets/icon.ico \
    --name="ProcessMonitorAgent" \
    --add-data="env.agent;." \
    src/main.py
```

#### macOS (.app)
```bash
# Basic compilation
pyinstaller --onefile --windowed src/main.py

# Advanced compilation
pyinstaller --onefile --windowed \
    --icon=assets/icon.icns \
    --name="ProcessMonitorAgent" \
    --add-data="env.agent:." \
    src/main.py
```

#### Linux (binary)
```bash
# Basic compilation
pyinstaller --onefile src/main.py

# Advanced compilation
pyinstaller --onefile \
    --name="ProcessMonitorAgent" \
    --add-data="env.agent:." \
    src/main.py
```

### 4. Build Scripts
Use the provided build scripts for automated compilation:

```bash
# Windows
build_scripts/build_windows.bat

# macOS
chmod +x build_scripts/build_mac.sh
./build_scripts/build_mac.sh

# Linux
chmod +x build_scripts/build_linux.sh
./build_scripts/build_linux.sh
```

### 5. Output Location
Compiled executables will be in the `dist/` directory:
- **Windows**: `dist/ProcessMonitorAgent.exe`
- **macOS**: `dist/ProcessMonitorAgent.app`
- **Linux**: `dist/ProcessMonitorAgent`

## Frontend Setup

### 1. Static Files
The frontend is already included in the Django project. Static files are served from:
- `backend/static/` - CSS, JavaScript, images
- `backend/templates/` - HTML templates

### 2. Customization
To modify the frontend:
1. Edit files in `frontend/` directory
2. Copy updated files to `backend/static/` and `backend/templates/`
3. Restart Django server

## Configuration

### Backend Configuration (env.config)
```bash
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,your-server-ip

# API Configuration
API_KEY=your-secure-api-key
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://your-domain.com

# Database
DATABASE_URL=sqlite:///db.sqlite3

# Process Monitoring
MAX_PROCESSES_PER_SNAPSHOT=1000
DATA_RETENTION_DAYS=30
SNAPSHOT_INTERVAL_SECONDS=60
```

### Agent Configuration (env.agent)
```bash
# Backend Connection
BACKEND_URL=http://your-server:8000/api/v1
API_KEY=your-secure-api-key

# Collection Settings
COLLECTION_INTERVAL=60
MAX_PROCESSES=1000

# Privacy Settings
ENABLE_PROCESS_FILTERING=true
FILTERED_PROCESS_NAMES=cursor,chrome,firefox,safari

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/agent.log
```

## Running the System

### 1. Start Backend
```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python manage.py runserver 0.0.0.0:8000
```

### 2. Run Agent
```bash
# Development mode
cd agent
source venv/bin/activate
python main.py

# Compiled executable
./dist/ProcessMonitorAgent  # or ProcessMonitorAgent.exe on Windows
```

### 3. Access Frontend
Open your web browser and navigate to:
- **Local**: http://localhost:8000
- **Network**: http://your-server-ip:8000

## Troubleshooting

### Common Issues

#### Django Server Won't Start
```bash
# Check if port is in use
netstat -an | grep 8000  # Linux/macOS
netstat -an | findstr 8000  # Windows

# Kill process using port
lsof -ti:8000 | xargs kill -9  # Linux/macOS
```

#### Agent Can't Connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/api/v1/hosts/summary/

# Verify API key in env.agent matches env.config
# Check firewall settings
# Verify network connectivity
```

#### PyInstaller Compilation Errors
```bash
# Clean previous builds
rm -rf build/ dist/ *.spec

# Reinstall PyInstaller
pip uninstall pyinstaller
pip install pyinstaller

# Check Python version compatibility
python --version
```

#### Process Filtering Not Working
```bash
# Verify env.agent configuration
cat env.agent | grep FILTERED_PROCESS_NAMES

# Check agent logs
tail -f logs/agent.log

# Test filtering manually
python test_filtering.py
```

### Performance Optimization

#### Backend
```bash
# Use production database (PostgreSQL/MySQL)
# Enable caching (Redis/Memcached)
# Use production WSGI server (Gunicorn/uWSGI)
# Enable database connection pooling
```

#### Agent
```bash
# Adjust collection interval
# Limit maximum processes collected
# Enable process filtering for privacy
# Use efficient data serialization
```

### Security Considerations
1. **Change default API keys** in production
2. **Use HTTPS** for production deployments
3. **Restrict CORS origins** to trusted domains
4. **Enable authentication** for sensitive endpoints
5. **Regular security updates** for dependencies

## Production Deployment

### 1. Environment Variables
```bash
# Set production environment
export DJANGO_SETTINGS_MODULE=process_monitor.settings
export DJANGO_ENV=production
export SECRET_KEY=your-production-secret-key
```

### 2. Database
```bash
# Use production database
pip install psycopg2-binary  # PostgreSQL
# or
pip install mysqlclient      # MySQL

# Update DATABASE_URL in env.config
```

### 3. Static Files
```bash
# Collect and serve static files
python manage.py collectstatic --noinput

# Use nginx or Apache for static file serving
```

### 4. Process Management
```bash
# Use systemd (Linux) or launchd (macOS)
# Monitor logs and restart on failure
# Set up health checks
```

## Support

For additional support:
1. Check the logs in `logs/` directory
2. Review the API documentation
3. Check the troubleshooting section above
4. Review the system architecture documentation

---

**Note**: This system is designed for educational and development purposes. For production use, ensure proper security measures, monitoring, and backup procedures are in place.
