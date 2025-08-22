# Process Monitoring System - Project Structure

## 📁 Complete Project Organization

```
process-monitor-system/
├── 📚 docs/                           # 📖 Documentation
│   ├── BUILD_INSTRUCTIONS.md          # 🛠️ Build and deployment guide
│   ├── ARCHITECTURE.md                # 🏗️ System architecture overview
│   ├── API_SPECIFICATIONS.md          # 📡 API documentation
│   └── ASSUMPTIONS_AND_LIMITATIONS.md # ⚠️ System constraints
│
├── 🤖 agent/                          # 🔍 Process monitoring agent
│   ├── src/                           # 📝 Source code
│   │   ├── process_collector.py       # 📊 Process data collection
│   │   ├── api_client.py              # 🌐 API communication
│   │   └── utils.py                   # 🛠️ Utility functions
│   ├── build_scripts/                 # 🔨 Build automation
│   │   ├── build_windows.bat          # 🪟 Windows build script
│   │   ├── build_mac.sh               # 🍎 macOS build script
│   │   └── build_linux.sh             # 🐧 Linux build script
│   ├── requirements.txt                # 📦 Python dependencies
│   ├── env.agent                      # ⚙️ Agent configuration
│   ├── env.example                    # 📋 Configuration template
│   └── main.py                        # 🚀 Main entry point
│
├── 🖥️ backend/                         # 🗄️ Django backend server
│   ├── process_monitor/               # ⚙️ Django project settings
│   │   ├── __init__.py
│   │   ├── settings.py                # 🔧 Project configuration
│   │   ├── urls.py                    # 🌐 URL routing
│   │   └── wsgi.py                    # 🌐 WSGI configuration
│   ├── process_api/                   # 📱 Main Django app
│   │   ├── __init__.py
│   │   ├── admin.py                   # 👑 Admin interface
│   │   ├── apps.py                    # 📱 App configuration
│   │   ├── models.py                  # 🗃️ Database models
│   │   ├── serializers.py             # 📤 Data serialization
│   │   ├── urls.py                    # 🔗 App URL routing
│   │   └── views.py                   # 👁️ API views
│   ├── static/                        # 🎨 Static files (CSS, JS, images)
│   │   ├── css/                       # 🎨 Stylesheets
│   │   ├── js/                        # 📜 JavaScript files
│   │   └── images/                    # 🖼️ Images and icons
│   ├── templates/                     # 📄 HTML templates
│   │   └── index.html                 # 🏠 Main page template
│   ├── requirements.txt                # 📦 Python dependencies
│   ├── env.config                     # ⚙️ Backend configuration
│   ├── manage.py                      # 🎮 Django management
│   └── db.sqlite3                     # 🗃️ SQLite database
│
├── 🌐 frontend/                        # 🎨 Frontend source files
│   ├── static/                        # 🎨 Source static files
│   │   ├── css/                       # 🎨 Source stylesheets
│   │   ├── js/                        # 📜 Source JavaScript
│   │   └── images/                    # 🖼️ Source images
│   ├── components/                    # 🧩 UI components
│   └── templates/                     # 📄 Source templates
│
├── 📖 README.md                        # 🏠 Main project documentation
├── 📋 PROJECT_STRUCTURE.md             # 📁 This file
└── 📝 .gitignore                       # 🚫 Git ignore rules
```

## 🔄 File Flow

### Development Workflow
```
frontend/ → backend/static/ → Django serves
     ↓              ↓
  Source files → Production files
```

### Agent Data Flow
```
System Processes → Agent Collection → API Submission → Database Storage
                                                      ↓
                                              Frontend Display
```

## 📋 Key Files Explained

### 🚀 Entry Points
- **`agent/main.py`**: Agent startup and main loop
- **`backend/manage.py`**: Django management commands
- **`frontend/index.html`**: Main web interface

### ⚙️ Configuration
- **`agent/env.agent`**: Agent settings (backend URL, API key, filtering)
- **`backend/env.config`**: Django settings (secret key, API key, debug mode)

### 🗃️ Data Models
- **`backend/process_api/models.py`**: Database schema (Host, Process, Snapshot)
- **`backend/process_api/views.py`**: API endpoints and business logic

### 🎨 User Interface
- **`frontend/static/js/app.js`**: Main application logic
- **`frontend/static/js/process-tree.js`**: Process tree visualization
- **`frontend/static/css/style.css`**: Custom styling

## 🧹 Clean Project Rules

### ✅ What to Keep
- Source code in appropriate directories
- Configuration files with examples
- Documentation in `docs/` folder
- Build scripts for all platforms
- Requirements files for dependencies

### ❌ What to Remove
- Test files and temporary scripts
- Cache directories (`__pycache__`, `.pyc`)
- Media files (user uploads)
- Database files (should be in `.gitignore`)
- Log files (should be in `.gitignore`)

### 🔄 What to Sync
- Frontend source → Backend static files
- Configuration templates → Actual configs
- Documentation updates → All relevant files

## 🚀 Quick Navigation

### For Developers
```bash
# Backend development
cd backend
python manage.py runserver

# Agent development
cd agent
python main.py

# Frontend development
cd frontend
# Edit files, then copy to backend/static/
```

### For Users
```bash
# Start the system
cd backend
python manage.py runserver

# Access web interface
open http://localhost:8000
```

### For Builders
```bash
# Build agent executable
cd agent
./build_scripts/build_mac.sh      # macOS
./build_scripts/build_linux.sh    # Linux
build_scripts\build_windows.bat   # Windows
```

## 📊 Project Status

### ✅ Completed
- [x] Cross-platform agent with process filtering
- [x] Django backend with REST API
- [x] Interactive web frontend
- [x] Process tree visualization
- [x] Comprehensive documentation
- [x] Build scripts for all platforms

### 🔄 In Progress
- [ ] Real-time updates (WebSockets)
- [ ] Advanced analytics and charts
- [ ] Process control capabilities

### 📋 Future Plans
- [ ] Multi-tenant support
- [ ] Mobile application
- [ ] Advanced security features
- [ ] Performance optimization

---

**This structure ensures a clean, professional, and maintainable project organization! 🎯**
