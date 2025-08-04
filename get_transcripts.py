#!/usr/bin/env python3
"""
Script om echte Voiceflow transcripts op te halen met nieuwe API implementatie
"""

import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv
from voiceflow_analytics import VoiceflowAnalytics

load_dotenv()

def get_voiceflow_transcripts_new_api():
    """Haal echte transcripts op van Voiceflow met nieuwe API"""
    
    print("🔍 Zoeken naar echte Voiceflow transcripts met nieuwe API...")
    print("="*60)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Test basis transcript ophalen
        print("📡 Testen van nieuwe transcript API...")
        
        response = analytics.get_all_project_transcripts(
            take=25,
            skip=0,
            order="DESC"
        )
        
        transcripts = response.get('transcripts', [])
        
        if not transcripts:
            print("❌ Geen transcripts gevonden!")
            print("Mogelijke oorzaken:")
            print("1. Project is niet gepubliceerd naar 'production'")
            print("2. Geen conversaties hebben plaatsgevonden")
            print("3. API key heeft geen toegang tot transcript data")
            return []
        
        print(f"✅ {len(transcripts)} transcripts gevonden!")
        
        # Toon eerste transcript details
        if transcripts:
            first_transcript = transcripts[0]
            print(f"\n📋 Eerste transcript details:")
            print(f"  ID: {first_transcript.get('id')}")
            print(f"  Session ID: {first_transcript.get('sessionID')}")
            print(f"  Created: {first_transcript.get('createdAt')}")
            print(f"  Properties: {len(first_transcript.get('properties', []))}")
            print(f"  Evaluations: {len(first_transcript.get('evaluations', []))}")
            print(f"  Recording URL: {'Ja' if first_transcript.get('recordingURL') else 'Nee'}")
        
        return transcripts
        
    except Exception as e:
        print(f"❌ Fout bij ophalen transcripts: {e}")
        return []

def get_all_transcripts_with_pagination():
    """Haal alle transcripts op met automatische paginering"""
    
    print("\n📥 Ophalen van alle transcripts met paginering...")
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Haal alle transcripts op
        all_transcripts = analytics.get_transcripts_with_pagination(
            batch_size=25,
            max_transcripts=None  # Alle transcripts
        )
        
        print(f"✅ Totaal {len(all_transcripts)} transcripts opgehaald!")
        
        return all_transcripts
        
    except Exception as e:
        print(f"❌ Fout bij paginering: {e}")
        return []

def get_transcripts_by_date_range(days_back: int = 30):
    """Haal transcripts op van de laatste X dagen"""
    
    print(f"\n📅 Ophalen van transcripts van laatste {days_back} dagen...")
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Bereken datum range
        end_date = datetime.now().isoformat()
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        transcripts = analytics.get_transcripts_by_date_range(
            start_date=start_date,
            end_date=end_date,
            batch_size=25
        )
        
        print(f"✅ {len(transcripts)} transcripts gevonden in laatste {days_back} dagen!")
        
        return transcripts
        
    except Exception as e:
        print(f"❌ Fout bij datum range ophalen: {e}")
        return []

def process_transcript_data_new(transcripts):
    """Verwerk transcript data voor dashboard (nieuwe API structuur)"""
    
    print(f"\n📊 Verwerken van {len(transcripts)} transcripts...")
    
    processed_data = []
    
    for transcript in transcripts:
        try:
            # Extract basis informatie
            transcript_info = {
                'transcript_id': transcript.get('id', 'unknown'),
                'session_id': transcript.get('sessionID', 'unknown'),
                'project_id': transcript.get('projectID', 'unknown'),
                'environment_id': transcript.get('environmentID', 'unknown'),
                'created_at': transcript.get('createdAt', datetime.now().isoformat()),
                'updated_at': transcript.get('updatedAt', ''),
                'ended_at': transcript.get('endedAt', ''),
                'expires_at': transcript.get('expiresAt', ''),
                'recording_url': transcript.get('recordingURL', ''),
                'has_recording': bool(transcript.get('recordingURL'))
            }
            
            # Extract properties
            properties = transcript.get('properties', [])
            transcript_info['total_properties'] = len(properties)
            
            # Extract property values
            for prop in properties:
                prop_name = prop.get('name', '')
                prop_value = prop.get('value', '')
                prop_type = prop.get('type', '')
                
                if prop_name:
                    transcript_info[f'property_{prop_name}'] = prop_value
                    transcript_info[f'property_{prop_name}_type'] = prop_type
            
            # Extract evaluations
            evaluations = transcript.get('evaluations', [])
            transcript_info['total_evaluations'] = len(evaluations)
            
            # Extract evaluation values
            for eval_item in evaluations:
                eval_name = eval_item.get('name', '')
                eval_value = eval_item.get('value', '')
                eval_type = eval_item.get('type', '')
                
                if eval_name:
                    transcript_info[f'evaluation_{eval_name}'] = eval_value
                    transcript_info[f'evaluation_{eval_name}_type'] = eval_type
            
            processed_data.append(transcript_info)
            
        except Exception as e:
            print(f"❌ Fout bij verwerken transcript: {e}")
            continue
    
    return processed_data

def analyze_transcripts_new(transcripts):
    """Analyseer transcript data (nieuwe API structuur)"""
    
    print(f"\n📈 Analyseren van {len(transcripts)} transcripts...")
    
    try:
        analytics = VoiceflowAnalytics()
        analysis = analytics.analyze_transcript_properties(transcripts)
        
        # Voeg extra analyses toe
        analysis['date_analysis'] = {}
        analysis['recording_analysis'] = analysis.get('recording_analysis', {})
        
        # Datum analyse
        date_counts = {}
        for transcript in transcripts:
            created = transcript.get('createdAt', '')
            if created:
                date = created[:10]  # YYYY-MM-DD
                date_counts[date] = date_counts.get(date, 0) + 1
        
        analysis['date_analysis']['daily_distribution'] = date_counts
        
        # Session analyse
        session_ids = set()
        for transcript in transcripts:
            session_id = transcript.get('sessionID', '')
            if session_id:
                session_ids.add(session_id)
        
        analysis['session_analysis']['unique_sessions'] = len(session_ids)
        
        return analysis
        
    except Exception as e:
        print(f"❌ Fout bij analyseren: {e}")
        return {}

def main():
    """Hoofdfunctie"""
    print("🚀 Voiceflow Transcript Fetcher (Nieuwe API)")
    print("="*60)
    
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
    
    # Test nieuwe API
    transcripts = get_voiceflow_transcripts_new_api()
    
    if not transcripts:
        print("\n❌ Geen transcripts gevonden!")
        return
    
    print(f"\n✅ {len(transcripts)} transcripts gevonden!")
    
    # Haal alle transcripts op met paginering
    all_transcripts = get_all_transcripts_with_pagination()
    
    if all_transcripts:
        print(f"📥 Totaal {len(all_transcripts)} transcripts opgehaald met paginering")
        
        # Verwerk data
        processed_transcripts = process_transcript_data_new(all_transcripts)
        
        # Analyseer data
        analysis = analyze_transcripts_new(all_transcripts)
        
        # Toon resultaten
        print(f"\n📊 Transcript Analyse:")
        print(f"Totaal transcripts: {analysis.get('total_transcripts', 0)}")
        
        # Properties analyse
        properties_analysis = analysis.get('properties_analysis', {})
        if properties_analysis:
            print(f"\n📊 Properties gevonden:")
            for prop_name, prop_data in properties_analysis.items():
                print(f"  - {prop_name}: {prop_data['count']} keer")
        
        # Evaluations analyse
        evaluations_analysis = analysis.get('evaluations_analysis', {})
        if evaluations_analysis:
            print(f"\n📊 Evaluations gevonden:")
            for eval_name, eval_data in evaluations_analysis.items():
                print(f"  - {eval_name}: {eval_data['count']} keer")
        
        # Recording analyse
        recording_analysis = analysis.get('recording_analysis', {})
        print(f"\n📊 Recording analyse:")
        print(f"  - Met recording: {recording_analysis.get('with_recording', 0)}")
        print(f"  - Zonder recording: {recording_analysis.get('without_recording', 0)}")
        
        # Session analyse
        session_analysis = analysis.get('session_analysis', {})
        print(f"\n📊 Session analyse:")
        print(f"  - Unieke sessions: {session_analysis.get('unique_session_count', 0)}")
        
        # Datum distributie
        date_analysis = analysis.get('date_analysis', {})
        daily_distribution = date_analysis.get('daily_distribution', {})
        if daily_distribution:
            print(f"\n📅 Dagelijkse distributie:")
            for date, count in sorted(daily_distribution.items()):
                print(f"  - {date}: {count} transcripts")
        
        # Sla data op
        with open('real_transcripts_new_api.json', 'w') as f:
            json.dump(processed_transcripts, f, indent=2, default=str)
        
        print(f"\n💾 Transcript data opgeslagen in 'real_transcripts_new_api.json'")
        print("🎯 Nu kun je het dashboard verversen om de echte transcript data te zien!")
    
    # Test datum range ophalen
    print(f"\n📅 Test datum range ophalen...")
    recent_transcripts = get_transcripts_by_date_range(days_back=7)
    if recent_transcripts:
        print(f"✅ {len(recent_transcripts)} transcripts gevonden in laatste 7 dagen")

if __name__ == "__main__":
    main() 