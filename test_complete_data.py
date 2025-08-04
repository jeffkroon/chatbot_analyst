#!/usr/bin/env python3
"""
Test script voor complete project data ophalen (zoals voorgesteld door Voiceflow bot)
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from voiceflow_analytics import VoiceflowAnalytics

# Load environment variables
load_dotenv()

def test_complete_project_data():
    """Test het ophalen van complete project data"""
    print("🚀 Test Complete Project Data Ophalen")
    print("="*60)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Haal complete project data op
        print("📊 Ophalen van complete project data...")
        
        complete_data = analytics.get_complete_project_data(
            batch_size=50,
            export_filename="complete_voiceflow_data.json"
        )
        
        print("✅ Complete project data succesvol opgehaald!")
        
        # Toon samenvatting
        summary = complete_data.get('summary', {})
        print(f"\n📊 Samenvatting:")
        print(f"  - Project ID: {complete_data.get('project_id')}")
        print(f"  - Opgehaald op: {complete_data.get('fetched_at')}")
        print(f"  - Totaal transcripts: {summary.get('total_transcripts', 0)}")
        print(f"  - Totaal evaluaties: {summary.get('total_evaluations', 0)}")
        print(f"  - Totaal evaluatie resultaten: {summary.get('total_evaluation_results', 0)}")
        
        # Toon evaluatie details
        evaluations = complete_data.get('evaluations', [])
        if evaluations:
            print(f"\n📋 Evaluatie Definities:")
            for eval_item in evaluations:
                print(f"  - {eval_item.get('name', 'Unknown')}: {eval_item.get('type', 'Unknown')}")
        
        # Toon evaluatie resultaten
        evaluation_results = complete_data.get('evaluation_results', [])
        if evaluation_results:
            print(f"\n📈 Evaluatie Resultaten (eerste 10):")
            for result in evaluation_results[:10]:
                print(f"  - {result['evaluation_name']}: {result['evaluation_value']} (cost: {result['evaluation_cost']})")
        
        # Toon transcript details
        transcripts = complete_data.get('transcripts', [])
        if transcripts:
            print(f"\n📝 Transcript Details (eerste 5):")
            for transcript in transcripts[:5]:
                transcript_id = transcript.get('id', 'Unknown')
                session_id = transcript.get('sessionID', 'Unknown')
                created = transcript.get('createdAt', 'Unknown')
                eval_count = len(transcript.get('evaluations', []))
                prop_count = len(transcript.get('properties', []))
                
                print(f"  - ID: {transcript_id}")
                print(f"    Session: {session_id}")
                print(f"    Created: {created}")
                print(f"    Evaluations: {eval_count}")
                print(f"    Properties: {prop_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def test_evaluations_only():
    """Test alleen evaluaties ophalen"""
    print("\n🧪 Test 2: Alleen Evaluaties")
    print("="*50)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Haal alleen evaluaties op
        evaluations = analytics.get_all_evaluations()
        
        print(f"✅ {len(evaluations.get('evaluations', []))} evaluaties gevonden")
        
        # Toon evaluatie details
        for eval_item in evaluations.get('evaluations', []):
            name = eval_item.get('name', 'Unknown')
            eval_type = eval_item.get('type', 'Unknown')
            description = eval_item.get('description', 'No description')
            
            print(f"\n📋 Evaluatie: {name}")
            print(f"  Type: {eval_type}")
            print(f"  Description: {description}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def test_paginated_fetch():
    """Test paginated fetch methode"""
    print("\n🧪 Test 3: Paginated Fetch")
    print("="*50)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Test paginated fetch
        transcripts = analytics.fetch_all_transcripts_paginated(
            batch_size=25
        )
        
        print(f"✅ {len(transcripts)} transcripts opgehaald met paginated fetch")
        
        # Toon unieke sessions
        session_ids = set()
        for transcript in transcripts:
            session_id = transcript.get('sessionID', '')
            if session_id:
                session_ids.add(session_id)
        
        print(f"Unieke sessions: {len(session_ids)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def analyze_evaluation_results(complete_data):
    """Analyseer evaluatie resultaten"""
    print("\n📊 Evaluatie Resultaten Analyse")
    print("="*50)
    
    evaluation_results = complete_data.get('evaluation_results', [])
    
    if not evaluation_results:
        print("❌ Geen evaluatie resultaten gevonden")
        return
    
    # Groepeer per evaluatie naam
    evaluation_stats = {}
    for result in evaluation_results:
        name = result['evaluation_name']
        value = result['evaluation_value']
        cost = result['evaluation_cost']
        
        if name not in evaluation_stats:
            evaluation_stats[name] = {
                'count': 0,
                'values': [],
                'total_cost': 0
            }
        
        evaluation_stats[name]['count'] += 1
        evaluation_stats[name]['values'].append(value)
        evaluation_stats[name]['total_cost'] += cost
    
    # Toon statistieken
    for name, stats in evaluation_stats.items():
        print(f"\n📋 {name}:")
        print(f"  Aantal: {stats['count']}")
        print(f"  Gemiddelde kosten: {stats['total_cost'] / stats['count']:.2f}")
        
        # Toon unieke waarden
        unique_values = set(stats['values'])
        print(f"  Unieke waarden: {len(unique_values)}")
        if len(unique_values) <= 10:
            print(f"  Waarden: {list(unique_values)}")

def main():
    """Hoofdfunctie"""
    print("🚀 Voiceflow Complete Data Test Suite")
    print("="*60)
    
    # Check environment
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = os.getenv('VOICEFLOW_PROJECT_ID')
    
    if not api_key:
        print("❌ VOICEFLOW_API_KEY niet gevonden in .env")
        return
    
    if not project_id or project_id == "your_project_id_here":
        print("❌ VOICEFLOW_PROJECT_ID niet correct geconfigureerd")
        return
    
    print(f"✅ Environment gecontroleerd")
    print(f"Project ID: {project_id}")
    
    # Run tests
    tests = [
        ("Complete project data", test_complete_project_data),
        ("Alleen evaluaties", test_evaluations_only),
        ("Paginated fetch", test_paginated_fetch)
    ]
    
    results = []
    complete_data = None
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            success = test_func()
            results.append((test_name, success))
            
            # Bewaar complete data voor analyse
            if test_name == "Complete project data" and success:
                try:
                    analytics = VoiceflowAnalytics()
                    complete_data = analytics.get_complete_project_data(batch_size=50)
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Onverwachte fout in {test_name}: {e}")
            results.append((test_name, False))
    
    # Toon resultaten
    print("\n" + "="*60)
    print("📊 Test Resultaten:")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nTotaal: {passed}/{len(results)} tests geslaagd")
    
    if passed == len(results):
        print("🎉 Alle tests geslaagd!")
        
        # Analyseer evaluatie resultaten als complete data beschikbaar is
        if complete_data:
            analyze_evaluation_results(complete_data)
    else:
        print("⚠️  Sommige tests gefaald. Controleer de implementatie.")

if __name__ == "__main__":
    main() 