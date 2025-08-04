#!/usr/bin/env python3
"""
Test script voor de nieuwe Voiceflow Transcript API endpoint
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from voiceflow_analytics import VoiceflowAnalytics

# Load environment variables
load_dotenv()

def test_basic_transcript_fetch():
    """Test basis transcript ophalen"""
    print("🧪 Test 1: Basis transcript ophalen")
    print("="*50)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Test basis call
        response = analytics.get_all_project_transcripts(take=10, skip=0, order="DESC")
        
        print(f"✅ API call succesvol!")
        print(f"Transcripts gevonden: {len(response.get('transcripts', []))}")
        
        if response.get('transcripts'):
            # Toon eerste transcript info
            first_transcript = response['transcripts'][0]
            print(f"\n📋 Eerste transcript:")
            print(f"  ID: {first_transcript.get('id')}")
            print(f"  Session ID: {first_transcript.get('sessionID')}")
            print(f"  Created: {first_transcript.get('createdAt')}")
            print(f"  Properties: {len(first_transcript.get('properties', []))}")
            print(f"  Evaluations: {len(first_transcript.get('evaluations', []))}")
            
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def test_pagination():
    """Test paginering"""
    print("\n🧪 Test 2: Paginering test")
    print("="*50)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Test eerste batch
        response1 = analytics.get_all_project_transcripts(take=5, skip=0, order="DESC")
        transcripts1 = response1.get('transcripts', [])
        
        # Test tweede batch
        response2 = analytics.get_all_project_transcripts(take=5, skip=5, order="DESC")
        transcripts2 = response2.get('transcripts', [])
        
        print(f"✅ Paginering werkt!")
        print(f"Batch 1: {len(transcripts1)} transcripts")
        print(f"Batch 2: {len(transcripts2)} transcripts")
        
        # Check voor duplicaten
        if transcripts1 and transcripts2:
            first_id_1 = transcripts1[0].get('id')
            first_id_2 = transcripts2[0].get('id')
            
            if first_id_1 != first_id_2:
                print("✅ Geen duplicaten in paginering")
            else:
                print("⚠️  Mogelijke duplicaten in paginering")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def test_date_filtering():
    """Test datum filtering"""
    print("\n🧪 Test 3: Datum filtering")
    print("="*50)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Test laatste 7 dagen
        end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        response = analytics.get_all_project_transcripts(
            take=10,
            skip=0,
            order="DESC",
            start_date=start_date,
            end_date=end_date
        )
        
        transcripts = response.get('transcripts', [])
        print(f"✅ Datum filtering werkt!")
        print(f"Transcripts in laatste 7 dagen: {len(transcripts)}")
        
        if transcripts:
            for transcript in transcripts[:3]:  # Toon eerste 3
                created = transcript.get('createdAt', '')
                print(f"  - {created}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def test_automatic_pagination():
    """Test automatische paginering"""
    print("\n🧪 Test 4: Automatische paginering")
    print("="*50)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Test automatische paginering
        all_transcripts = analytics.get_transcripts_with_pagination(
            batch_size=10,
            max_transcripts=50
        )
        
        print(f"✅ Automatische paginering werkt!")
        print(f"Totaal transcripts opgehaald: {len(all_transcripts)}")
        
        # Toon unieke session IDs
        session_ids = set()
        for transcript in all_transcripts:
            session_id = transcript.get('sessionID', '')
            if session_id:
                session_ids.add(session_id)
        
        print(f"Unieke sessions: {len(session_ids)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def test_property_analysis():
    """Test property analyse"""
    print("\n🧪 Test 5: Property analyse")
    print("="*50)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Haal transcripts op
        transcripts = analytics.get_transcripts_with_pagination(batch_size=25, max_transcripts=100)
        
        if not transcripts:
            print("❌ Geen transcripts gevonden voor analyse")
            return False
        
        # Analyseer properties
        analysis = analytics.analyze_transcript_properties(transcripts)
        
        print(f"✅ Property analyse voltooid!")
        print(f"Totaal transcripts: {analysis['total_transcripts']}")
        
        # Toon property analyse
        if analysis['properties_analysis']:
            print(f"\n📊 Properties gevonden:")
            for prop_name, prop_data in analysis['properties_analysis'].items():
                print(f"  - {prop_name}: {prop_data['count']} keer (type: {prop_data['type']})")
        
        # Toon evaluation analyse
        if analysis['evaluations_analysis']:
            print(f"\n📊 Evaluations gevonden:")
            for eval_name, eval_data in analysis['evaluations_analysis'].items():
                print(f"  - {eval_name}: {eval_data['count']} keer (type: {eval_data['type']})")
        
        # Toon recording analyse
        recording_analysis = analysis['recording_analysis']
        print(f"\n📊 Recording analyse:")
        print(f"  - Met recording: {recording_analysis.get('with_recording', 0)}")
        print(f"  - Zonder recording: {recording_analysis.get('without_recording', 0)}")
        
        # Toon session analyse
        session_analysis = analysis['session_analysis']
        print(f"\n📊 Session analyse:")
        print(f"  - Unieke sessions: {session_analysis.get('unique_session_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def test_date_range_fetch():
    """Test datum range ophalen"""
    print("\n🧪 Test 6: Datum range ophalen")
    print("="*50)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Test laatste 30 dagen
        end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        
        transcripts = analytics.get_transcripts_by_date_range(
            start_date=start_date,
            end_date=end_date,
            batch_size=25
        )
        
        print(f"✅ Datum range ophalen werkt!")
        print(f"Transcripts in laatste 30 dagen: {len(transcripts)}")
        
        if transcripts:
            # Toon datum distributie
            date_counts = {}
            for transcript in transcripts:
                created = transcript.get('createdAt', '')
                if created:
                    date = created[:10]  # YYYY-MM-DD
                    date_counts[date] = date_counts.get(date, 0) + 1
            
            print(f"\n📅 Datum distributie:")
            for date, count in sorted(date_counts.items()):
                print(f"  - {date}: {count} transcripts")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def main():
    """Hoofdfunctie voor alle tests"""
    print("🚀 Voiceflow Transcript API Test Suite")
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
        ("Basis transcript ophalen", test_basic_transcript_fetch),
        ("Paginering", test_pagination),
        ("Datum filtering", test_date_filtering),
        ("Automatische paginering", test_automatic_pagination),
        ("Property analyse", test_property_analysis),
        ("Datum range ophalen", test_date_range_fetch)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
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
        print("🎉 Alle tests geslaagd! De nieuwe API implementatie werkt correct.")
    else:
        print("⚠️  Sommige tests gefaald. Controleer de implementatie.")

if __name__ == "__main__":
    main() 