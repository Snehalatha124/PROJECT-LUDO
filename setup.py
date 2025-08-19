#!/usr/bin/env python3
"""
Setup script for Ludo Performance Testing Suite
Automates the initial setup process for both backend and frontend
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {command}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def check_node_version():
    """Check if Node.js version is compatible"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version} detected")
            return True
    except:
        pass
    
    print("❌ Node.js 16+ is required")
    return False

def setup_backend():
    """Setup backend environment"""
    print("\n🔧 Setting up Backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create virtual environment
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print("📦 Creating Python virtual environment...")
        if not run_command("python -m venv venv", cwd=backend_dir):
            return False
    
    # Install Python dependencies
    print("📦 Installing Python dependencies...")
    pip_cmd = "venv\\Scripts\\pip" if os.name == 'nt' else "venv/bin/pip"
    if not run_command(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir):
        return False
    
    # Create .env file
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print("🔐 Creating .env file...")
        env_content = """# Gemini AI Configuration
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=true
HOST=0.0.0.0
PORT=5000

# Test Configuration
MAX_CONCURRENT_TESTS=10
DEFAULT_TEST_DURATION=60
DEFAULT_NUM_USERS=100

# Deployment Configuration
BACKEND_URL=http://localhost:5000
FRONTEND_URL=http://localhost:3000
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created with your Gemini API key")
        print("💡 You can add your OpenRouter API key to enable image analysis")
    else:
        print("✅ .env file already exists")
    
    return True

def setup_frontend():
    """Setup frontend environment"""
    print("\n🎨 Setting up Frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install Node.js dependencies
    print("📦 Installing Node.js dependencies...")
    if not run_command("npm install", cwd=frontend_dir):
        return False
    
    # Create .env file
    env_file = frontend_dir / ".env"
    if not env_file.exists():
        print("🔐 Creating frontend .env file...")
        env_content = """# Frontend Environment Configuration

# Backend API URL
# For local development:
REACT_APP_BACKEND_URL=http://localhost:5000

# For production deployment (set in Vercel dashboard):
# REACT_APP_BACKEND_URL=https://your-backend.vercel.app

# Environment
REACT_APP_ENV=development

# Feature flags
REACT_APP_ENABLE_AI_ANALYSIS=true
REACT_APP_ENABLE_REAL_TIME_MONITORING=true
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Frontend .env file created")
    else:
        print("✅ Frontend .env file already exists")
    
    return True

def create_startup_scripts():
    """Create startup scripts for different platforms"""
    print("\n🚀 Creating startup scripts...")
    
    # Windows batch script
    bat_content = """@echo off
echo Starting Ludo Performance Testing Suite...

echo Starting Backend...
start "Backend" cmd /k "cd backend && venv\\Scripts\\activate && python app.py"

echo Starting Frontend...
start "Frontend" cmd /k "cd frontend && npm start"

echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
pause
"""
    
    with open("start.bat", 'w') as f:
        f.write(bat_content)
    
    # Unix/Linux shell script
    sh_content = """#!/bin/bash
echo "Starting Ludo Performance Testing Suite..."

# Function to cleanup background processes
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo "Starting Backend..."
cd backend
source venv/bin/activate
python app.py &
BACKEND_PID=$!

echo "Starting Frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "Both servers are starting..."
echo "Backend: http://localhost:5000"
echo "Frontend: http://localhost:3000"
echo "Press Ctrl+C to stop both servers"

# Wait for both processes
wait
"""
    
    with open("start.sh", 'w') as f:
        f.write(sh_content)
    
    # Make shell script executable
    os.chmod("start.sh", 0o755)
    
    print("✅ Startup scripts created")

def main():
    """Main setup function"""
    print("🚀 Ludo Performance Testing Suite Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        return False
    
    if not check_node_version():
        return False
    
    # Setup backend
    if not setup_backend():
        print("❌ Backend setup failed")
        return False
    
    # Setup frontend
    if not setup_frontend():
        print("❌ Frontend setup failed")
        return False
    
    # Create startup scripts
    create_startup_scripts()
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Your Gemini API key is already configured in backend/.env")
    print("2. Optional: Add your OpenRouter API key to backend/.env for image analysis")
    print("3. Start the application:")
    print("   - Windows: Double-click start.bat")
    print("   - Unix/Linux: ./start.sh")
    print("4. Open http://localhost:3000 in your browser")
    
    print("\n🔐 API Keys Status:")
    print("✅ Gemini API: Configured")
    print("⚠️  OpenRouter API: Add your key to backend/.env for image analysis")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 