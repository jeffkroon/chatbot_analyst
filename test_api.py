#!/usr/bin/env python3
"""
Test script voor Voiceflow API endpoints
"""

import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_api_endpoints():
    """Test alle API endpoints met echte Project ID"""
    
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = "688666ba51c1d0b2cc252cbe"  # Je echte Project ID
    
    print("🧪 Test Voiceflow API Endpoints")
    print("="*50)
    print(f"Project ID: {project_id}")
    print(f"API Key: {api_key[:10]}..." if api_key else "❌ API Key niet gevonden")
    print()
    
    if not api_key:
        print("❌ VOICEFLOW_API_KEY niet gevonden in .env")
        return
    
    # Test verschillende endpoints
    endpoints = [
        {
            'name': 'Dialog Manager - User State',
            'url': 'https://general-runtime.voiceflow.com/state/user/test',
            'method': 'GET',
            'headers': {'Authorization': api_key}
        },
        {
            'name': 'Analytics - Evaluations',
            'url': f'https://analytics-api.voiceflow.com/v1/transcript-evaluation/project/{project_id}',
            'method': 'GET',
            'headers': {'Authorization': f'Bearer {api_key}'}
        },
        {
            'name': 'Analytics - Transcripts',
            'url': f'https://analytics-api.voiceflow.com/v1/transcript/project/{project_id}',
            'method': 'POST',
            'headers': {'Authorization': f'Bearer {api_key}'},
            'data': {'projectID': project_id, 'limit': 10, 'offset': 0}
        }
    ]
    
    for endpoint in endpoints:
        print(f"🔍 Test: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(endpoint['url'], headers=endpoint['headers'])
            elif endpoint['method'] == 'POST':
                response = requests.post(endpoint['url'], json=endpoint.get('data', {}), headers=endpoint['headers'])
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Werkt!")
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if 'evaluations' in data:
                            print(f"  Evaluations gevonden: {len(data['evaluations'])}")
                        elif 'transcripts' in data:
                            print(f"  Transcripts gevonden: {len(data['transcripts'])}")
                        else:
                            print(f"  Keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"  Items: {len(data)}")
                except:
                    print("  Response is geen JSON")
            else:
                print(f"❌ Fout: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 50)

def test_evaluations_api():
    """Test specifiek de evaluations API"""
    
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = "688666ba51c1d0b2cc252cbe"
    
    print("\n🎯 Test Evaluations API")
    print("="*30)
    
    if not api_key:
        print("❌ API Key niet gevonden")
        return
    
    # Test evaluations endpoint
    url = f'https://analytics-api.voiceflow.com/v1/transcript-evaluation/project/{project_id}'
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            evaluations = data.get('evaluations', [])
            print(f"✅ {len(evaluations)} evaluations gevonden!")
            
            for eval_item in evaluations:
                print(f"  - {eval_item.get('name', 'Unknown')} ({eval_item.get('type', 'unknown')})")
        else:
            print(f"❌ Fout: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_endpoints()
    test_evaluations_api() 