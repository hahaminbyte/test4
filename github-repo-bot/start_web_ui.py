#!/usr/bin/env python3
"""
GitHub Repository Enhancement Bot - Web UI Launcher
Easy startup script for the web interface
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    
    print("🔍 Checking dependencies...")
    
    try:
        import flask
        import github
        import rich
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("📦 Installing dependencies...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements_web.txt"
            ], check=True)
            print("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False

def start_web_server():
    """Start the Flask web server"""
    
    print("🚀 Starting GitHub Repository Enhancement Bot...")
    print("🌐 Web interface will be available at: http://localhost:5000")
    
    # Start Flask app
    try:
        from app import app
        
        # Open browser after a short delay
        def open_browser():
            time.sleep(2)
            webbrowser.open("http://localhost:5000")
        
        import threading
        threading.Thread(target=open_browser).start()
        
        # Start Flask server
        app.run(debug=False, host='0.0.0.0', port=5000)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main launcher function"""
    
    print("=" * 60)
    print("🤖 GitHub Repository Enhancement Bot - Web UI")
    print("=" * 60)
    print()
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ Please run this script from the github-repo-bot directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    print()
    print("📋 Features Available:")
    print("   • Analyze any local project folder")
    print("   • AI-powered deep project analysis")
    print("   • Contextual commit history from real files")
    print("   • GitHub issues and pull requests")
    print("   • Multiple developer personas")
    print()
    
    input("Press Enter to start the web interface...")
    
    # Start web server
    start_web_server()

if __name__ == "__main__":
    main()