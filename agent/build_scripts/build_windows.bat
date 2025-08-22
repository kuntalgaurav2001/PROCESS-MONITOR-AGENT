@echo off
REM Build script for Windows
REM Compiles the process monitoring agent into a standalone executable

echo 🚀 Building Process Monitor Agent for Windows...

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ❌ PyInstaller not found. Installing...
    pip install pyinstaller
)

REM Navigate to agent directory
cd /d "%~dp0\.."

REM Create build directory
if not exist "build" mkdir build

REM Build the executable
echo 📦 Building executable with PyInstaller...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "ProcessMonitorAgent" ^
    --distpath build ^
    --workpath build\work ^
    --specpath build ^
    --add-data "config;config" ^
    --hidden-import psutil ^
    --hidden-import requests ^
    --hidden-import dotenv ^
    main.py

if errorlevel 1 (
    echo ❌ Build failed!
    pause
    exit /b 1
)

echo ✅ Build completed successfully!
echo 📁 Executable location: build\ProcessMonitorAgent.exe
echo 💡 You can now run: build\ProcessMonitorAgent.exe
pause
