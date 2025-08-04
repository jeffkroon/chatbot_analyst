#!/usr/bin/env python3
"""
Comprehensive test script voor Voiceflow Analytics systeem
Test elke component stap voor stap
"""

import os
import sys
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def print_header(title):
    """Print een mooie header"""
    print("\n" + "="*50)
    print(f"🧪 {title}")
    print("="*50)

def print_success(message):
    """Print success bericht"""
    print(f"✅ {message}")

def print_error(message):
    """Print error bericht"""
    print(f"❌ {message}")

def print_warning(message):
    """Print warning bericht"""
    print(f"⚠️ {message}")

def print_info(message):
    """Print info bericht"""
    print(f"ℹ️ {message}")

def test_environment():
    """Test environment configuratie"""
    print_header("Environment Test")
    
    # Check .env file
    if not os.path.exists('.env'):
        print_error(".env bestand niet gevonden!")
        print_info("Maak een .env bestand aan op basis van env_example.txt")
        return False
    
    # Check required environment variables
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = os.getenv('VOICEFLOW_PROJECT_ID')
    
    if not api_key:
        print_error("VOICEFLOW_API_KEY niet gevonden in .env")
        return False
    
    if not project_id:
        print_error("VOICEFLOW_PROJECT_ID niet gevonden in .env")
        return False
    
    print_success("Environment variabelen gevonden")
    print_info(f"API Key: {api_key[:10]}...")
    print_info(f"Project ID: {project_id}")
    return True

def test_dependencies():
    """Test of alle dependencies geïnstalleerd zijn"""
    print_header("Dependencies Test")
    
    required_packages = [
        'requests', 'python-dotenv', 'streamlit', 
        'pandas', 'plotly', 'supabase'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print_success(f"{package} geïnstalleerd")
        except ImportError:
            print_error(f"{package} niet geïnstalleerd")
            missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"Installeer ontbrekende packages: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_voiceflow_api():
    """Test Voiceflow API connectie"""
    print_header("Voiceflow API Test")
    
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = os.getenv('VOICEFLOW_PROJECT_ID')
    
    if not api_key or not project_id:
        print_error("API key of Project ID ontbreekt")
        return False
    
    # Test 1: Check API key format
    if not api_key.startswith('VF.'):
        print_warning("API key lijkt niet in het juiste formaat (moet beginnen met VF.)")
    
    # Test 2: Test basic API call
    try:
        url = "https://analytics-api.voiceflow.com/v1/transcript-evaluation"
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print_success("Voiceflow API connectie succesvol")
            evaluations = response.json().get('evaluations', [])
            print_info(f"Gevonden evaluaties: {len(evaluations)}")
            return True
        elif response.status_code == 401:
            print_error("API key is ongeldig of verlopen")
            return False
        elif response.status_code == 403:
            print_error("Geen toegang tot dit project")
            return False
        else:
            print_error(f"API call gefaald: {response.status_code} - {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Netwerk fout: {e}")
        return False

def test_project_access():
    """Test toegang tot specifiek project"""
    print_header("Project Access Test")
    
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = os.getenv('VOICEFLOW_PROJECT_ID')
    
    try:
        # Test transcripts ophalen
        url = "https://analytics-api.voiceflow.com/v1/transcript"
        headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "projectID": project_id,
            "limit": 10,
            "offset": 0
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            transcripts = response.json().get('transcripts', [])
            print_success(f"Project toegang succesvol")
            print_info(f"Transcripts gevonden: {len(transcripts)}")
            
            if transcripts:
                print_info("Project heeft conversatie data")
                return True
            else:
                print_warning("Geen transcripts gevonden - project is mogelijk niet gepubliceerd")
                return False
        else:
            print_error(f"Project toegang gefaald: {response.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Project test fout: {e}")
        return False

def test_local_modules():
    """Test lokale modules"""
    print_header("Local Modules Test")
    
    modules = [
        'voiceflow_analytics',
        'database', 
        'chatbot_analyzer'
    ]
    
    for module in modules:
        try:
            __import__(module)
            print_success(f"{module}.py geladen")
        except ImportError as e:
            print_error(f"Kan {module}.py niet laden: {e}")
            return False
    
    return True

def test_database():
    """Test database functionaliteit"""
    print_header("Database Test")
    
    try:
        from database import AnalyticsDatabase
        
        db = AnalyticsDatabase()
        print_success("Database module geïnitialiseerd")
        
        # Test data opslaan
        test_data = {
            'user_id': 'test_user',
            'timestamp': datetime.now().isoformat(),
            'request_type': 'text',
            'response_text': 'Test bericht',
            'course_mentioned': 'Test Cursus'
        }
        
        db.store_conversation_log(test_data)
        print_success("Test data opgeslagen")
        
        # Test data ophalen
        summary = db.get_analytics_summary(days_back=7)
        print_success("Analytics samenvatting opgehaald")
        
        return True
        
    except Exception as e:
        print_error(f"Database test gefaald: {e}")
        return False

def test_analytics():
    """Test analytics functionaliteit"""
    print_header("Analytics Test")
    
    try:
        from voiceflow_analytics import VoiceflowAnalytics
        
        analytics = VoiceflowAnalytics()
        print_success("Analytics module geïnitialiseerd")
        
        # Test evaluaties ophalen
        evaluations = analytics.get_all_evaluations()
        print_info(f"Gevonden evaluaties: {len(evaluations)}")
        
        # Test transcripts ophalen
        transcripts = analytics.get_project_transcripts(limit=5)
        print_info(f"Transcripts gevonden: {len(transcripts)}")
        
        return True
        
    except Exception as e:
        print_error(f"Analytics test gefaald: {e}")
        return False

def test_chatbot():
    """Test chatbot functionaliteit"""
    print_header("Chatbot Test")
    
    try:
        from chatbot_analyzer import ChatbotAnalyzer
        
        chatbot = ChatbotAnalyzer()
        print_success("Chatbot geïnitialiseerd")
        
        # Test snelle chat
        response = chatbot.process_message("Hallo")
        print_success("Snelle chat werkt")
        
        # Test analyse detectie
        is_analysis = chatbot.is_analysis_request("Analyseer cursussen")
        if is_analysis:
            print_success("Analyse detectie werkt")
        else:
            print_error("Analyse detectie werkt niet")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Chatbot test gefaald: {e}")
        return False

def run_full_test():
    """Voer alle tests uit"""
    print("🚀 Voiceflow Analytics System Test")
    print("="*60)
    
    tests = [
        ("Environment", test_environment),
        ("Dependencies", test_dependencies),
        ("Voiceflow API", test_voiceflow_api),
        ("Project Access", test_project_access),
        ("Local Modules", test_local_modules),
        ("Database", test_database),
        ("Analytics", test_analytics),
        ("Chatbot", test_chatbot)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Test {test_name} crashte: {e}")
            results.append((test_name, False))
    
    # Print samenvatting
    print_header("Test Samenvatting")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"✅ Geslaagd: {passed}/{total}")
    print(f"❌ Gefaald: {total - passed}/{total}")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    if passed == total:
        print_success("Alle tests geslaagd! Systeem is klaar voor gebruik.")
    else:
        print_warning("Sommige tests gefaald. Controleer de foutmeldingen hierboven.")
    
    return passed == total

def quick_fix_suggestions():
    """Geef suggesties voor veelvoorkomende problemen"""
    print_header("Quick Fix Suggesties")
    
    print("🔧 Als API tests falen:")
    print("1. Controleer je Voiceflow API key in .env")
    print("2. Zorg dat je project gepubliceerd is naar 'production'")
    print("3. Controleer of je project ID correct is")
    
    print("\n🔧 Als database tests falen:")
    print("1. Systeem valt terug op lokale JSON storage")
    print("2. Dit zou automatisch moeten werken")
    
    print("\n🔧 Als dependencies ontbreken:")
    print("1. Run: pip install -r requirements.txt")
    print("2. Of installeer handmatig: pip install requests python-dotenv streamlit pandas plotly")

if __name__ == "__main__":
    success = run_full_test()
    
    if not success:
        print("\n" + "="*60)
        quick_fix_suggestions()
    
    print("\n🎯 Volgende stappen:")
    print("1. Als alle tests slagen: python run_dashboard.py")
    print("2. Als tests falen: Controleer de foutmeldingen hierboven")
    print("3. Voor help: Lees de README.md") 