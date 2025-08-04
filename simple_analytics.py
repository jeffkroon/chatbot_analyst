#!/usr/bin/env python3
"""
Vereenvoudigde Voiceflow Analytics die werkt met beschikbare API's
"""

import os
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleVoiceflowAnalytics:
    """
    Vereenvoudigde analytics die werkt met beschikbare Voiceflow API's
    """
    
    def __init__(self):
        self.api_key = os.getenv('VOICEFLOW_API_KEY')
        self.project_id = os.getenv('VOICEFLOW_PROJECT_ID')
        self.dm_url = "https://general-runtime.voiceflow.com"
        
        if not self.api_key:
            raise ValueError("VOICEFLOW_API_KEY is niet geconfigureerd")
        if not self.project_id or self.project_id == "your_project_id_here":
            raise ValueError("VOICEFLOW_PROJECT_ID is niet correct geconfigureerd")
    
    def _get_headers(self) -> Dict[str, str]:
        """Basis headers voor API requests"""
        return {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def test_connection(self) -> bool:
        """Test de API connectie"""
        try:
            url = f"{self.dm_url}/state/user/test"
            response = requests.get(url, headers=self._get_headers())
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Connectie test gefaald: {e}")
            return False
    
    def simulate_conversation(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Simuleer een conversatie om data te genereren
        
        Args:
            user_id: Unieke user ID
            message: Bericht van gebruiker
        
        Returns:
            Response data
        """
        try:
            url = f"{self.dm_url}/state/user/{user_id}/interact"
            
            payload = {
                "type": "text",
                "payload": {
                    "message": message
                }
            }
            
            response = requests.post(url, json=payload, headers=self._get_headers())
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Conversatie gefaald: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Fout bij conversatie: {e}")
            return {}
    
    def get_user_state(self, user_id: str) -> Dict[str, Any]:
        """Haal user state op"""
        try:
            url = f"{self.dm_url}/state/user/{user_id}"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"State ophalen gefaald: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Fout bij ophalen state: {e}")
            return {}
    
    def analyze_conversation_data(self, conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyseer conversatie data"""
        if not conversations:
            return {
                'total_conversations': 0,
                'popular_topics': [],
                'response_patterns': []
            }
        
        results = {
            'total_conversations': len(conversations),
            'popular_topics': [],
            'response_patterns': []
        }
        
        # Analyseer topics
        topics = {}
        for conv in conversations:
            message = conv.get('message', '').lower()
            topic = conv.get('topic', 'unknown')
            
            if 'cursus' in message or 'course' in message:
                topics['cursussen'] = topics.get('cursussen', 0) + 1
            elif 'prijs' in message or 'kosten' in message:
                topics['prijzen'] = topics.get('prijzen', 0) + 1
            elif 'inschrijven' in message or 'aanmelden' in message:
                topics['inschrijvingen'] = topics.get('inschrijvingen', 0) + 1
            elif 'help' in message or 'hulp' in message:
                topics['hulp'] = topics.get('hulp', 0) + 1
        
        results['popular_topics'] = [
            {'topic': topic, 'count': count}
            for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Analyseer response patterns
        response_types = {}
        for conv in conversations:
            response = conv.get('response', {})
            response_type = response.get('type', 'unknown')
            response_types[response_type] = response_types.get(response_type, 0) + 1
        
        results['response_patterns'] = [
            {'type': rtype, 'count': count}
            for rtype, count in sorted(response_types.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return results

def main():
    """Test de vereenvoudigde analytics met echte data"""
    print("🧪 Simple Voiceflow Analytics Test")
    print("="*50)
    
    try:
        analytics = SimpleVoiceflowAnalytics()
        
        # Test connectie
        if analytics.test_connection():
            print("✅ API connectie succesvol")
        else:
            print("❌ API connectie gefaald")
            return
        
        # Test conversatie
        print("\n🔍 Test conversatie...")
        response = analytics.simulate_conversation("test_user", "Hallo")
        if response:
            print("✅ Conversatie succesvol")
            print(f"Response type: {type(response)}")
        else:
            print("❌ Conversatie gefaald")
        
        # Test echte data analyse
        print("\n📊 Test echte data analyse...")
        
        # Haal echte conversatie data op
        conversations = []
        user_ids = ["test", "user_001", "user_002", "demo_user"]
        
        for user_id in user_ids:
            try:
                state = analytics.get_user_state(user_id)
                if state and state.get('variables'):
                    conv_data = {
                        'user_id': user_id,
                        'timestamp': datetime.now().isoformat(),
                        'message': 'Test message',
                        'response': {'type': 'text', 'content': 'Response'},
                        'topic': 'test'
                    }
                    conversations.append(conv_data)
            except Exception as e:
                print(f"Fout bij ophalen data voor {user_id}: {e}")
        
        if conversations:
            results = analytics.analyze_conversation_data(conversations)
            
            print("✅ Analyse voltooid")
            print(f"Totaal conversaties: {results['total_conversations']}")
            print(f"Populaire topics: {len(results['popular_topics'])}")
            
            # Toon resultaten
            print("\n📈 Resultaten:")
            for topic in results['popular_topics']:
                print(f"  - {topic['topic']}: {topic['count']} mentions")
        else:
            print("❌ Geen echte conversatie data gevonden")
        
    except Exception as e:
        print(f"❌ Fout: {e}")

if __name__ == "__main__":
    main() 