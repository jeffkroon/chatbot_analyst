#!/usr/bin/env python3
"""
Script om echte conversaties te genereren met je Voiceflow chatbot
"""

import os
import requests
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

def simulate_conversation_flow(api_key, user_id, messages):
    """Simuleer een volledige conversatie flow"""
    
    print(f"\n💬 Simuleer conversatie voor user: {user_id}")
    print("-" * 40)
    
    headers = {
        'Authorization': api_key,
        'Content-Type': 'application/json'
    }
    
    conversation_data = {
        'user_id': user_id,
        'timestamp': datetime.now().isoformat(),
        'messages': [],
        'responses': []
    }
    
    for i, message in enumerate(messages):
        try:
            url = f"https://general-runtime.voiceflow.com/state/user/{user_id}/interact"
            
            payload = {
                "type": "text",
                "payload": {
                    "message": message
                }
            }
            
            print(f"📤 Bericht {i+1}: '{message}'")
            
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"📥 Response ontvangen (status: 200)")
                
                # Sla bericht en response op
                conversation_data['messages'].append(message)
                conversation_data['responses'].append(data)
                
                # Wacht even tussen berichten
                time.sleep(1)
                
            else:
                print(f"❌ Fout bij bericht {i+1}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error bij bericht {i+1}: {e}")
    
    return conversation_data

def main():
    """Hoofdfunctie"""
    print("🚀 Voiceflow Conversation Generator")
    print("="*50)
    
    api_key = os.getenv('VOICEFLOW_API_KEY')
    
    if not api_key:
        print("❌ VOICEFLOW_API_KEY niet gevonden in .env")
        return
    
    # Verschillende conversatie scenarios
    conversation_scenarios = [
        {
            'user_id': 'user_ai_course',
            'messages': [
                "Hallo",
                "Ik ben geïnteresseerd in AI cursussen",
                "Welke AI cursussen zijn er beschikbaar?",
                "Wat kost de AI cursus?",
                "Hoe kan ik me inschrijven?",
                "Bedankt voor de informatie"
            ]
        },
        {
            'user_id': 'user_python_course',
            'messages': [
                "Hallo",
                "Ik wil Python leren",
                "Hebben jullie een Python cursus?",
                "Wat is de inhoud van de cursus?",
                "Wat zijn de kosten?",
                "Oké, ik ga het overwegen"
            ]
        },
        {
            'user_id': 'user_web_development',
            'messages': [
                "Hallo",
                "Ik zoek een web development cursus",
                "Welke technologieën leer je?",
                "Is er ook JavaScript inbegrepen?",
                "Hoe lang duurt de cursus?",
                "Bedankt"
            ]
        },
        {
            'user_id': 'user_data_science',
            'messages': [
                "Hallo",
                "Ik ben geïnteresseerd in data science",
                "Welke tools leer je in de cursus?",
                "Is Python inbegrepen?",
                "Wat zijn de carrière mogelijkheden?",
                "Interessant, ik ga het bekijken"
            ]
        },
        {
            'user_id': 'user_digital_marketing',
            'messages': [
                "Hallo",
                "Ik zoek een digital marketing cursus",
                "Welke platforms behandel je?",
                "Is er ook SEO inbegrepen?",
                "Wat zijn de kosten?",
                "Bedankt voor de info"
            ]
        }
    ]
    
    all_conversations = []
    
    print(f"🎯 Start genereren van {len(conversation_scenarios)} conversaties...")
    
    for scenario in conversation_scenarios:
        conversation = simulate_conversation_flow(
            api_key, 
            scenario['user_id'], 
            scenario['messages']
        )
        all_conversations.append(conversation)
        
        # Wacht even tussen conversaties
        time.sleep(2)
    
    # Sla alle conversaties op
    with open('generated_conversations.json', 'w') as f:
        json.dump(all_conversations, f, indent=2, default=str)
    
    print(f"\n✅ {len(all_conversations)} conversaties gegenereerd!")
    print("💾 Data opgeslagen in 'generated_conversations.json'")
    
    # Toon samenvatting
    print("\n📊 Conversatie Samenvatting:")
    for conv in all_conversations:
        user_id = conv['user_id']
        message_count = len(conv['messages'])
        print(f"  - {user_id}: {message_count} berichten")
    
    print("\n🎯 Nu kun je het dashboard verversen om de nieuwe data te zien!")

if __name__ == "__main__":
    main() 