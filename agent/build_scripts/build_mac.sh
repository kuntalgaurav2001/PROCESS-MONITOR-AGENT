#!/bin/bash
# Build script for macOS
# Compiles the process monitoring agent into a standalone executable

set -e

echo "🚀 Building Process Monitor Agent for macOS..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Navigate to agent directory
cd "$(dirname "$0")/.."

# Create build directory
mkdir -p build

# Build the executable
echo "📦 Building executable with PyInstaller..."
pyinstaller \
    --onefile \
    --windowed \
    --name "ProcessMonitorAgent" \
    --distpath build \
    --workpath build/work \
    --specpath build \
    --add-data "config:config" \
    --hidden-import psutil \
    --hidden-import requests \
    --hidden-import dotenv \
    main.py

# Make executable
chmod +x build/ProcessMonitorAgent

echo "✅ Build completed successfully!"
echo "📁 Executable location: build/ProcessMonitorAgent"
echo "💡 You can now run: ./build/ProcessMonitorAgent"
