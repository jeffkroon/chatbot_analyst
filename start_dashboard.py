#!/usr/bin/env python3
"""
Voiceflow Dashboard Launcher
"""

import os
import sys
import subprocess
from pathlib import Path

def check_environment():
    """Controleer environment setup"""
    print("🔍 Controleer environment...")
    
    # Check .env file
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env bestand niet gevonden")
        print("Maak een .env bestand aan met:")
        print("VOICEFLOW_API_KEY=jouw_api_key_hier")
        print("VOICEFLOW_PROJECT_ID=jouw_project_id_hier")
        return False
    
    # Check virtual environment
    if not os.getenv('VIRTUAL_ENV'):
        print("⚠️  Virtual environment niet actief")
        print("Run: source .venv/bin/activate")
        return False
    
    print("✅ Environment OK")
    return True

def check_dependencies():
    """Controleer dependencies"""
    print("🔍 Controleer dependencies...")
    
    required_packages = ['streamlit', 'pandas', 'plotly', 'requests', 'python-dotenv']
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} geïnstalleerd")
        except ImportError:
            print(f"❌ {package} niet geïnstalleerd")
            return False
    
    print("✅ Alle dependencies OK")
    return True

def main():
    """Start het dashboard"""
    print("🚀 Voiceflow Analytics Dashboard")
    print("="*50)
    
    # Controleer environment
    if not check_environment():
        print("\n❌ Environment niet correct geconfigureerd")
        print("Fix de problemen hierboven en probeer opnieuw")
        return
    
    # Controleer dependencies
    if not check_dependencies():
        print("\n❌ Dependencies ontbreken")
        print("Run: pip install -r requirements.txt")
        return
    
    # Start dashboard
    print("\n🌐 Start dashboard...")
    print("Dashboard wordt geopend in je browser")
    print("Druk Ctrl+C om te stoppen")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "voiceflow_dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard gestopt")
    except Exception as e:
        print(f"\n❌ Fout bij starten dashboard: {e}")

if __name__ == "__main__":
    main() 