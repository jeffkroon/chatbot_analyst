#!/usr/bin/env python3
"""
Test verschillende Voiceflow API endpoints om de juiste te vinden
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_endpoint(url, method="GET", headers=None, data=None):
    """Test een API endpoint"""
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        
        print(f"🔍 {method} {url}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        print()
        
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = os.getenv('VOICEFLOW_PROJECT_ID')
    
    if not api_key:
        print("❌ VOICEFLOW_API_KEY niet gevonden in .env")
        return
    
    headers = {
        "Authorization": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    print("🧪 Voiceflow API Endpoint Test")
    print("="*50)
    
    # Test verschillende endpoints
    endpoints = [
        # Analytics API endpoints
        ("https://analytics-api.voiceflow.com/v1/transcript-evaluation", "GET"),
        ("https://analytics-api.voiceflow.com/v1/transcript", "POST"),
        
        # Dialog Manager API endpoints
        ("https://general-runtime.voiceflow.com/state/user/test/interact", "POST"),
        ("https://general-runtime.voiceflow.com/state/user/test", "GET"),
        
        # Project API endpoints
        ("https://api.voiceflow.com/v2/projects", "GET"),
        ("https://api.voiceflow.com/v2/projects/" + project_id, "GET"),
        
        # Transcript API endpoints
        ("https://api.voiceflow.com/v2/projects/" + project_id + "/transcripts", "GET"),
    ]
    
    for url, method in endpoints:
        if method == "POST" and "transcript" in url:
            data = {"projectID": project_id, "limit": 10, "offset": 0}
        elif method == "POST":
            data = {"type": "launch"}
        else:
            data = None
        
        success = test_endpoint(url, method, headers, data)
        
        if success:
            print(f"✅ {url} werkt!")
        else:
            print(f"❌ {url} werkt niet")
        
        print("-" * 50)

if __name__ == "__main__":
    main() 