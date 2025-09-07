#!/usr/bin/env python3
"""
Local development runner for the Code Review Service
"""

import os
import sys
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required packages are installed"""
    try:
        import fastapi
        import sqlalchemy
        import openai
        import uvicorn
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has API key"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("Please copy env.example to .env and add your OpenAI API key")
        return False
    
    with open(env_file) as f:
        content = f.read()
        if "OPENAI_API_KEY=sk-" not in content:
            print("❌ OpenAI API key not found in .env file")
            print("Please add your OpenAI API key to the .env file")
            return False
    
    print("✅ Environment configuration looks good")
    return True

def run_service():
    """Run the FastAPI service"""
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"📁 Data directory: {data_dir.absolute()}")
    
    print("🚀 Starting Code Review Service...")
    print("📍 Service will be available at: http://localhost:8001")
    print("📚 API docs will be available at: http://localhost:8001/docs")
    print("🛑 Press Ctrl+C to stop the service")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8001"
        ])
    except KeyboardInterrupt:
        print("\n👋 Service stopped by user")
    except Exception as e:
        print(f"❌ Error starting service: {e}")

def main():
    print("Code Review Service - Local Development Runner")
    print("=" * 50)
    
    if not check_requirements():
        return
    
    if not check_env_file():
        return
    
    run_service()

if __name__ == "__main__":
    main()
