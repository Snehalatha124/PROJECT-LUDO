#!/usr/bin/env python3
"""
Simple script to create .env files with API keys
"""

import os
from pathlib import Path

def create_backend_env():
    """Create backend .env file"""
    backend_dir = Path("backend")
    env_file = backend_dir / ".env"
    
    if env_file.exists():
        print("⚠️  Backend .env file already exists")
        return
    
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
    
    print("✅ Backend .env file created")
    print("⚠️  IMPORTANT: Replace 'your-gemini-api-key-here' with your real Gemini API key")
    print("💡 Get your API key from: https://makersuite.google.com/app/apikey")

def create_frontend_env():
    """Create frontend .env file"""
    frontend_dir = Path("frontend")
    env_file = frontend_dir / ".env"
    
    if env_file.exists():
        print("⚠️  Frontend .env file already exists")
        return
    
    env_content = """# Frontend Environment Configuration

# Backend API URL
# For local development:
REACT_APP_BACKEND_URL=http://localhost:5000

# For production deployment (set in Netlify dashboard):
# REACT_APP_BACKEND_URL=https://your-backend.onrender.com

# Environment
REACT_APP_ENV=development

# Feature flags
REACT_APP_ENABLE_AI_ANALYSIS=true
REACT_APP_ENABLE_REAL_TIME_MONITORING=true
"""
    
    with open(env_file, 'w') as f:
        f.write(env_content)
    
    print("✅ Frontend .env file created")

def main():
    print("🔐 Creating .env files...")
    
    # Create backend .env
    create_backend_env()
    
    # Create frontend .env
    create_frontend_env()
    
    print("\n🎉 .env files created successfully!")
    print("\n📋 Next Steps:")
    print("1. Get your Gemini API key from: https://makersuite.google.com/app/apikey")
    print("2. Replace 'your-gemini-api-key-here' in backend/.env with your real key")
    print("3. Set GEMINI_API_KEY in your Render dashboard for production")

if __name__ == "__main__":
    main() 