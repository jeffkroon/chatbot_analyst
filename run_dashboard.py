#!/usr/bin/env python3
"""
Voiceflow Analytics Dashboard Launcher
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Controleer of alle dependencies geïnstalleerd zijn"""
    try:
        import streamlit
        import pandas
        import plotly
        import requests
        import dotenv
        print("✅ Alle dependencies zijn geïnstalleerd")
        return True
    except ImportError as e:
        print(f"❌ Ontbrekende dependency: {e}")
        print("Installeer dependencies met: pip install -r requirements.txt")
        return False

def check_env_file():
    """Controleer of .env bestand bestaat"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env bestand niet gevonden")
        print("Maak een .env bestand aan op basis van env_example.txt")
        print("Voeg je Voiceflow API key en Project ID toe")
        return False
    return True

def main():
    """Start het dashboard"""
    print("🚀 Voiceflow Analytics Dashboard")
    print("=" * 40)
    
    # Controleer dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Controleer .env bestand
    if not check_env_file():
        print("\n📝 Voorbeeld .env configuratie:")
        print("VOICEFLOW_API_KEY=your_api_key_here")
        print("VOICEFLOW_PROJECT_ID=your_project_id_here")
        print("\nGa naar je Voiceflow dashboard om deze waarden te vinden.")
        sys.exit(1)
    
    # Start dashboard
    print("🌐 Start dashboard...")
    print("Dashboard wordt geopend in je browser")
    print("Druk Ctrl+C om te stoppen")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard gestopt")
    except Exception as e:
        print(f"❌ Fout bij starten dashboard: {e}")

if __name__ == "__main__":
    main() 