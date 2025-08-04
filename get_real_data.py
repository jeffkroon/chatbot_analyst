#!/usr/bin/env python3
"""
Script om echte Voiceflow data op te halen
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def test_api_endpoints():
    """Test verschillende API endpoints om echte data te vinden"""
    
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = os.getenv('VOICEFLOW_PROJECT_ID')
    
    print("🔍 Zoeken naar echte Voiceflow data...")
    print("="*50)
    
    if not api_key:
        print("❌ VOICEFLOW_API_KEY niet gevonden in .env")
        return
    
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }
    
    # Test verschillende endpoints
    endpoints = [
        # Dialog Manager API - voor conversaties
        {
            'name': 'Dialog Manager - User State',
            'url': f'https://general-runtime.voiceflow.com/state/user/test',
            'method': 'GET'
        },
        {
            'name': 'Dialog Manager - Interact',
            'url': f'https://general-runtime.voiceflow.com/state/user/test/interact',
            'method': 'POST',
            'data': {'type': 'launch'}
        },
        # Project API - voor project info
        {
            'name': 'Project Info',
            'url': f'https://api.voiceflow.com/v2/projects/{project_id}',
            'method': 'GET'
        },
        # Analytics API - voor transcripts (als beschikbaar)
        {
            'name': 'Analytics - Transcripts',
            'url': f'https://analytics-api.voiceflow.com/v1/transcript',
            'method': 'POST',
            'data': {'projectID': project_id, 'limit': 10}
        }
    ]
    
    working_endpoints = []
    
    for endpoint in endpoints:
        print(f"\n🔍 Test: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=headers)
            elif endpoint['method'] == 'POST':
                response = requests.post(endpoint['url'], json=endpoint.get('data', {}), headers=headers)
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Werkt!")
                working_endpoints.append(endpoint)
                
                # Toon een sample van de response
                try:
                    data = response.json()
                    print(f"Response type: {type(data)}")
                    if isinstance(data, dict):
                        print(f"Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"Items: {len(data)}")
                except:
                    print("Response is geen JSON")
            else:
                print(f"❌ Fout: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return working_endpoints

def get_conversation_history(api_key, user_id="test_user"):
    """Haal conversatie geschiedenis op"""
    
    print(f"\n📊 Ophalen conversatie geschiedenis voor user: {user_id}")
    
    # Test verschillende user IDs
    user_ids = [
        user_id,
        "user_001",
        "user_002", 
        "demo_user",
        "test"
    ]
    
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }
    
    conversations = []
    
    for uid in user_ids:
        try:
            url = f"https://general-runtime.voiceflow.com/state/user/{uid}"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ User {uid}: Data gevonden")
                
                # Extract conversatie data
                conv_data = {
                    'user_id': uid,
                    'timestamp': datetime.now().isoformat(),
                    'state_data': data,
                    'has_conversation': bool(data.get('stack', []))
                }
                conversations.append(conv_data)
                
            else:
                print(f"❌ User {uid}: Geen data ({response.status_code})")
                
        except Exception as e:
            print(f"❌ User {uid}: Error - {e}")
    
    return conversations

def simulate_real_conversations(api_key):
    """Simuleer echte conversaties om data te genereren"""
    
    print("\n💬 Simuleren van echte conversaties...")
    
    test_messages = [
        "Hallo",
        "Ik wil meer weten over cursussen",
        "Welke AI cursussen zijn er?",
        "Wat kost de Python cursus?",
        "Hoe kan ik me inschrijven?",
        "Bedankt voor de informatie"
    ]
    
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }
    
    conversations = []
    
    for i, message in enumerate(test_messages):
        user_id = f"test_user_{i}"
        
        try:
            # Start conversatie
            url = f"https://general-runtime.voiceflow.com/state/user/{user_id}/interact"
            
            payload = {
                "type": "text",
                "payload": {
                    "message": message
                }
            }
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ '{message}' -> Response ontvangen")
                
                conv_data = {
                    'user_id': user_id,
                    'message': message,
                    'timestamp': datetime.now().isoformat(),
                    'response': data,
                    'traces': data.get('traces', [])
                }
                conversations.append(conv_data)
                
            else:
                print(f"❌ '{message}' -> Fout: {response.status_code}")
                
        except Exception as e:
            print(f"❌ '{message}' -> Error: {e}")
    
    return conversations

def analyze_conversation_data(conversations):
    """Analyseer de echte conversatie data"""
    
    print(f"\n📈 Analyseren van {len(conversations)} conversaties...")
    
    analysis = {
        'total_conversations': len(conversations),
        'successful_conversations': 0,
        'response_types': {},
        'message_patterns': [],
        'course_mentions': []
    }
    
    for conv in conversations:
        if conv.get('response'):
            analysis['successful_conversations'] += 1
            
            # Analyseer response types
            traces = conv.get('traces', [])
            for trace in traces:
                trace_type = trace.get('type', 'unknown')
                analysis['response_types'][trace_type] = analysis['response_types'].get(trace_type, 0) + 1
            
            # Zoek naar course mentions
            message = conv.get('message', '').lower()
            if any(word in message for word in ['cursus', 'course', 'ai', 'python', 'web', 'data']):
                analysis['course_mentions'].append({
                    'user_id': conv['user_id'],
                    'message': conv['message'],
                    'timestamp': conv['timestamp']
                })
    
    return analysis

def main():
    """Hoofdfunctie"""
    print("🚀 Voiceflow Real Data Fetcher")
    print("="*50)
    
    # Test API endpoints
    working_endpoints = test_api_endpoints()
    
    if not working_endpoints:
        print("\n❌ Geen werkende endpoints gevonden!")
        return
    
    print(f"\n✅ {len(working_endpoints)} werkende endpoints gevonden")
    
    # Haal echte data op
    api_key = os.getenv('VOICEFLOW_API_KEY')
    
    # 1. Conversatie geschiedenis
    conversations = get_conversation_history(api_key)
    
    # 2. Simuleer nieuwe conversaties
    new_conversations = simulate_real_conversations(api_key)
    conversations.extend(new_conversations)
    
    # 3. Analyseer data
    if conversations:
        analysis = analyze_conversation_data(conversations)
        
        print(f"\n📊 Analyse Resultaten:")
        print(f"Totaal conversaties: {analysis['total_conversations']}")
        print(f"Succesvolle conversaties: {analysis['successful_conversations']}")
        print(f"Response types: {analysis['response_types']}")
        print(f"Course mentions: {len(analysis['course_mentions'])}")
        
        # Sla data op voor dashboard
        with open('real_conversation_data.json', 'w') as f:
            json.dump(conversations, f, indent=2, default=str)
        
        print(f"\n💾 Data opgeslagen in 'real_conversation_data.json'")
        
    else:
        print("\n❌ Geen conversatie data gevonden")

if __name__ == "__main__":
    main() 