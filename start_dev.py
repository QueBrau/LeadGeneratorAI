#!/usr/bin/env python3
"""
Development startup script for LeadGeneratorAI
Starts both backend API server and frontend React app
"""

import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def run_backend():
    """Start the Flask backend server"""
    print("🐍 Starting Python backend server...")
    try:
        # Make sure we have the required packages
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True, capture_output=True)
        
        # Start the Flask server
        subprocess.run([sys.executable, "api_server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend server failed: {e}")
        print("Make sure you have all requirements installed:")
        print("pip install -r requirements.txt")

def run_frontend():
    """Start the React frontend server"""
    frontend_dir = Path("lead-finder-frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return
    
    print("⚛️  Starting React frontend server...")
    try:
        # Change to frontend directory
        os.chdir(frontend_dir)
        
        # Install npm dependencies if needed
        if not Path("node_modules").exists():
            print("📦 Installing npm dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        # Start React development server
        subprocess.run(["npm", "start"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend server failed: {e}")
        print("Make sure you have Node.js and npm installed")
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm")

def main():
    print("🚀 LeadGeneratorAI Development Server")
    print("=" * 50)
    
    choice = input("""
What would you like to start?
1. Backend only (Flask API server)
2. Frontend only (React app)  
3. Both (recommended for development)

Enter choice (1-3): """).strip()
    
    if choice == "1":
        run_backend()
    elif choice == "2":
        run_frontend()
    elif choice == "3":
        print("🔄 Starting both servers...")
        print("Backend will start on: http://localhost:5000")
        print("Frontend will start on: http://localhost:3000")
        print("\nPress Ctrl+C to stop both servers")
        
        # Start backend in a separate thread
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Give backend time to start
        time.sleep(3)
        
        # Start frontend (this will block)
        run_frontend()
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()