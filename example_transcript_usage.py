#!/usr/bin/env python3
"""
Voorbeeld script voor het gebruik van de nieuwe Voiceflow Transcript API
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from voiceflow_analytics import VoiceflowAnalytics

# Load environment variables
load_dotenv()

def example_basic_usage():
    """Voorbeeld van basis transcript ophalen"""
    print("📋 Voorbeeld 1: Basis transcript ophalen")
    print("="*50)
    
    analytics = VoiceflowAnalytics()
    
    # Haal eerste 10 transcripts op
    response = analytics.get_all_project_transcripts(
        take=10,
        skip=0,
        order="DESC"
    )
    
    transcripts = response.get('transcripts', [])
    print(f"✅ {len(transcripts)} transcripts opgehaald")
    
    if transcripts:
        # Toon details van eerste transcript
        first = transcripts[0]
        print(f"\n📋 Eerste transcript:")
        print(f"  ID: {first.get('id')}")
        print(f"  Session: {first.get('sessionID')}")
        print(f"  Created: {first.get('createdAt')}")
        print(f"  Properties: {len(first.get('properties', []))}")
        print(f"  Evaluations: {len(first.get('evaluations', []))}")

def example_pagination():
    """Voorbeeld van paginering"""
    print("\n📄 Voorbeeld 2: Paginering")
    print("="*50)
    
    analytics = VoiceflowAnalytics()
    
    # Haal alle transcripts op met automatische paginering
    all_transcripts = analytics.get_transcripts_with_pagination(
        batch_size=25,
        max_transcripts=100  # Maximum 100 transcripts
    )
    
    print(f"✅ {len(all_transcripts)} transcripts opgehaald met paginering")
    
    # Toon unieke sessions
    session_ids = set()
    for transcript in all_transcripts:
        session_id = transcript.get('sessionID', '')
        if session_id:
            session_ids.add(session_id)
    
    print(f"Unieke sessions: {len(session_ids)}")

def example_date_filtering():
    """Voorbeeld van datum filtering"""
    print("\n📅 Voorbeeld 3: Datum filtering")
    print("="*50)
    
    analytics = VoiceflowAnalytics()
    
    # Haal transcripts van laatste 7 dagen op
    end_date = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    transcripts = analytics.get_transcripts_by_date_range(
        start_date=start_date,
        end_date=end_date,
        batch_size=25
    )
    
    print(f"✅ {len(transcripts)} transcripts gevonden in laatste 7 dagen")
    
    if transcripts:
        # Toon datum distributie
        date_counts = {}
        for transcript in transcripts:
            created = transcript.get('createdAt', '')
            if created:
                date = created[:10]  # YYYY-MM-DD
                date_counts[date] = date_counts.get(date, 0) + 1
        
        print(f"\n📊 Dagelijkse distributie:")
        for date, count in sorted(date_counts.items()):
            print(f"  - {date}: {count} transcripts")

def example_property_analysis():
    """Voorbeeld van property analyse"""
    print("\n📊 Voorbeeld 4: Property analyse")
    print("="*50)
    
    analytics = VoiceflowAnalytics()
    
    # Haal transcripts op
    transcripts = analytics.get_transcripts_with_pagination(
        batch_size=50,
        max_transcripts=50
    )
    
    if not transcripts:
        print("❌ Geen transcripts gevonden")
        return
    
    # Analyseer properties
    analysis = analytics.analyze_transcript_properties(transcripts)
    
    print(f"✅ Analyse voltooid voor {analysis['total_transcripts']} transcripts")
    
    # Toon property analyse
    properties = analysis.get('properties_analysis', {})
    if properties:
        print(f"\n📊 Properties gevonden:")
        for prop_name, prop_data in properties.items():
            print(f"  - {prop_name}: {prop_data['count']} keer (type: {prop_data['type']})")
    
    # Toon evaluation analyse
    evaluations = analysis.get('evaluations_analysis', {})
    if evaluations:
        print(f"\n📊 Evaluations gevonden:")
        for eval_name, eval_data in evaluations.items():
            print(f"  - {eval_name}: {eval_data['count']} keer (type: {eval_data['type']})")
    
    # Toon recording analyse
    recording = analysis.get('recording_analysis', {})
    print(f"\n📊 Recording analyse:")
    print(f"  - Met recording: {recording.get('with_recording', 0)}")
    print(f"  - Zonder recording: {recording.get('without_recording', 0)}")

def example_advanced_filtering():
    """Voorbeeld van geavanceerde filtering"""
    print("\n🔍 Voorbeeld 5: Geavanceerde filtering")
    print("="*50)
    
    analytics = VoiceflowAnalytics()
    
    # Voorbeeld filters
    filters = [
        {
            "id": "sessionID",
            "op": "exists"
        },
        {
            "id": "createdAt",
            "op": "gte",
            "value": (datetime.now() - timedelta(days=30)).isoformat()
        }
    ]
    
    try:
        response = analytics.get_all_project_transcripts(
            take=25,
            skip=0,
            order="DESC",
            filters=filters
        )
        
        transcripts = response.get('transcripts', [])
        print(f"✅ {len(transcripts)} transcripts gevonden met filters")
        
    except Exception as e:
        print(f"❌ Fout bij filtering: {e}")

def example_save_to_file():
    """Voorbeeld van data opslaan"""
    print("\n💾 Voorbeeld 6: Data opslaan")
    print("="*50)
    
    analytics = VoiceflowAnalytics()
    
    # Haal transcripts op
    transcripts = analytics.get_transcripts_with_pagination(
        batch_size=25,
        max_transcripts=100
    )
    
    if not transcripts:
        print("❌ Geen transcripts gevonden")
        return
    
    # Verwerk data voor opslag
    processed_data = []
    for transcript in transcripts:
        processed_transcript = {
            'id': transcript.get('id'),
            'session_id': transcript.get('sessionID'),
            'created_at': transcript.get('createdAt'),
            'properties_count': len(transcript.get('properties', [])),
            'evaluations_count': len(transcript.get('evaluations', [])),
            'has_recording': bool(transcript.get('recordingURL'))
        }
        processed_data.append(processed_transcript)
    
    # Sla op in JSON bestand
    filename = f"transcripts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(processed_data, f, indent=2, default=str)
    
    print(f"✅ {len(processed_data)} transcripts opgeslagen in '{filename}'")

def main():
    """Hoofdfunctie voor alle voorbeelden"""
    print("🚀 Voiceflow Transcript API Voorbeelden")
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
    
    # Run voorbeelden
    examples = [
        ("Basis transcript ophalen", example_basic_usage),
        ("Paginering", example_pagination),
        ("Datum filtering", example_date_filtering),
        ("Property analyse", example_property_analysis),
        ("Geavanceerde filtering", example_advanced_filtering),
        ("Data opslaan", example_save_to_file)
    ]
    
    for example_name, example_func in examples:
        try:
            print(f"\n{'='*60}")
            example_func()
        except Exception as e:
            print(f"❌ Fout in {example_name}: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 Alle voorbeelden voltooid!")
    print("💡 Bekijk de gegenereerde bestanden voor meer details.")

if __name__ == "__main__":
    main() 