#!/usr/bin/env python3
"""
AI Bot Analytics API client voor het ophalen en analyseren van chatbot data
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIBotAnalytics:
    """
    AI Bot Analytics API client
    
    Deze class biedt toegang tot de AI Bot Analytics API voor het ophalen
    van transcripts, evaluaties en andere analytics data.
    """
    
    def __init__(self):
        self.api_key = os.getenv('VOICEFLOW_API_KEY')
        self.project_id = os.getenv('VOICEFLOW_PROJECT_ID')
        self.base_url = "https://analytics-api.voiceflow.com/v1"
        self.dm_url = "https://general-runtime.voiceflow.com"
        
        if not self.api_key:
            raise ValueError("VOICEFLOW_API_KEY is niet geconfigureerd")
        if not self.project_id:
            raise ValueError("VOICEFLOW_PROJECT_ID is niet geconfigureerd")
    
    def _get_headers(self) -> Dict[str, str]:
        """Basis headers voor API requests"""
        return {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_transcript_evaluation(self, name: str, prompt: str, 
                                   description: str = None, 
                                   evaluation_type: str = "text") -> Dict[str, Any]:
        """
        Maak een transcript evaluatie aan voor het analyseren van conversaties
        
        Args:
            name: Naam van de evaluatie
            prompt: De prompt voor de AI evaluatie
            description: Beschrijving van de evaluatie
            evaluation_type: Type evaluatie (text, boolean, number)
        
        Returns:
            Dict met evaluatie data
        """
        url = f"{self.base_url}/transcript-evaluation"
        
        payload = {
            "projectID": self.project_id,
            "name": name,
            "description": description,
            "enabled": True,
            "prompt": prompt,
            "settings": {
                "type": evaluation_type
            }
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            logger.info(f"Transcript evaluatie '{name}' aangemaakt")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fout bij aanmaken transcript evaluatie: {e}")
            raise
    
    def get_all_evaluations(self, project_id: str = None) -> Dict[str, Any]:
        """
        Haal alle evaluatie definities op voor een project
        
        Args:
            project_id: Project ID (gebruikt self.project_id als None)
            
        Returns:
            Dict met evaluatie data
        """
        if project_id is None:
            project_id = self.project_id
            
        url = f"{self.base_url}/transcript-evaluation/project/{project_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Evaluaties opgehaald: {len(data.get('evaluations', []))} gevonden")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fout bij ophalen evaluaties: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
    
    def run_evaluation_for_transcript(self, evaluation_id: str, transcript_id: str) -> Dict[str, Any]:
        """
        Voer een evaluatie uit op een specifiek transcript
        
        Args:
            evaluation_id: ID van de evaluatie
            transcript_id: ID van het transcript
        
        Returns:
            Dict met evaluatie resultaten
        """
        url = f"{self.base_url}/transcript-evaluation/{evaluation_id}/run"
        
        payload = {
            "transcriptID": transcript_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Fout bij uitvoeren evaluatie: {e}")
            raise
    
    def get_project_transcripts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Haal alle transcripts op voor dit project
        
        Args:
            limit: Maximum aantal transcripts om op te halen
            offset: Offset voor paginering
        
        Returns:
            List van transcript data
        """
        url = f"{self.base_url}/transcript"
        
        payload = {
            "projectID": self.project_id,
            "limit": limit,
            "offset": offset
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers())
            response.raise_for_status()
            return response.json().get('transcripts', [])
        except requests.exceptions.RequestException as e:
            logger.error(f"Fout bij ophalen transcripts: {e}")
            return []
    
    def get_legacy_transcripts(self, 
                             project_id: str = None,
                             tag: str = None,
                             date_range: str = None,
                             start_date: str = None,
                             end_date: str = None) -> List[Dict[str, Any]]:
        """
        Haal transcripts op via de legacy v2 API (echte chat gesprekken)
        
        Args:
            project_id: Project ID (gebruikt self.project_id als None)
            tag: Filter op tag (bv. 'system.reviewed')
            date_range: Range filter ('Today', 'Yesterday', 'Last 7 Days', 'Last 30 days', 'All time')
            start_date: Start datum (YYYY-MM-DD)
            end_date: Eind datum (YYYY-MM-DD)
            
        Returns:
            List van transcript data met echte chat gesprekken
        """
        if project_id is None:
            project_id = self.project_id
            
        url = f"https://api.voiceflow.com/v2/transcripts/{project_id}"
        
        # Query parameters
        params = {}
        if tag:
            params['tag'] = tag
        if date_range:
            params['range'] = date_range
        if start_date:
            params['startDate'] = start_date
        if end_date:
            params['endDate'] = end_date
        
        # Headers voor legacy API
        headers = {
            'Authorization': self.api_key,
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            transcripts = response.json()
            logger.info(f"Legacy transcripts opgehaald: {len(transcripts)} gevonden")
            return transcripts
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fout bij ophalen legacy transcripts: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise

    def get_legacy_transcript_metadata(self, transcript_id: str) -> Dict[str, Any]:
        """
        Haal transcript metadata op via legacy API (basis info zonder dialog)
        
        Args:
            transcript_id: ID van het transcript
            
        Returns:
            Dict met transcript metadata (session info, user info, etc.)
        """
        url = f"https://api.voiceflow.com/v2/transcripts/{transcript_id}"
        
        headers = {
            'Authorization': self.api_key,
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Legacy transcript metadata opgehaald voor {transcript_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fout bij ophalen legacy transcript metadata: {e}")
            raise

    def get_legacy_transcript_details(self, transcript_id: str) -> Dict[str, Any]:
        """
        Haal gedetailleerde transcript data op via legacy API
        
        Args:
            transcript_id: ID van het transcript
            
        Returns:
            Dict met volledige transcript data inclusief chat berichten
        """
        url = f"https://api.voiceflow.com/v2/transcripts/{transcript_id}"
        
        headers = {
            'Authorization': self.api_key,
            'Accept': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Legacy transcript details opgehaald voor {transcript_id}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fout bij ophalen legacy transcript details: {e}")
            raise

    def get_transcript_messages(self, transcript_id: str) -> List[Dict[str, Any]]:
        """
        Haal alleen de chat berichten op van een transcript
        
        Args:
            transcript_id: ID van het transcript
            
        Returns:
            List van chat berichten/logs
        """
        try:
            # Gebruik de reguliere transcript endpoint
            url = f"{self.base_url}/transcript/{transcript_id}"
            response = requests.get(url, headers=self._get_headers())
            response.raise_for_status()
            full_data = response.json()
            logger.info(f"Transcript data opgehaald voor {transcript_id}")
            
            # De transcript data zit in een 'transcript' key
            if 'transcript' in full_data:
                transcript_data = full_data['transcript']
            else:
                transcript_data = full_data
            
            # Probeer verschillende mogelijke velden voor messages/logs
            messages = transcript_data.get('logs', [])
            if not messages:
                messages = transcript_data.get('messages', [])
            if not messages:
                messages = transcript_data.get('chat', [])
            if not messages:
                messages = transcript_data.get('conversation', [])
            if not messages:
                messages = transcript_data.get('interactions', [])
            if not messages:
                messages = transcript_data.get('traces', [])
            if not messages:
                messages = transcript_data.get('steps', [])
            if not messages:
                messages = transcript_data.get('events', [])
            
            logger.info(f"Chat logs gevonden: {len(messages)} voor transcript {transcript_id}")
            logger.info(f"Available keys in transcript_data: {list(transcript_data.keys()) if isinstance(transcript_data, dict) else 'Not a dict'}")
            return messages
            
        except Exception as e:
            logger.error(f"Fout bij ophalen chat logs: {e}")
            return []

    def get_all_project_transcripts(self, 
                                  take: int = 25, 
                                  skip: int = 0, 
                                  order: str = "DESC",
                                  session_id: Optional[str] = None,
                                  environment_id: Optional[str] = None,
                                  start_date: Optional[str] = None,
                                  end_date: Optional[str] = None,
                                  filters: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Haal alle project transcripts op volgens de nieuwe API specificatie
        
        Args:
            take: Maximum aantal transcripts (1-100, default 25)
            skip: Offset voor paginering (default 0)
            order: Sortering (ASC/DESC, default DESC)
            session_id: Filter op specifieke session ID
            environment_id: Filter op environment ID
            start_date: Start datum filter (ISO format)
            end_date: Eind datum filter (ISO format)
            filters: Array van filter objecten
            
        Returns:
            Dict met transcripts data volgens API specificatie
        """
        url = f"{self.base_url}/transcript/project/{self.project_id}"
        
        # Query parameters
        params = {
            'take': min(max(take, 1), 100),  # Ensure 1-100 range
            'skip': max(skip, 0),  # Ensure non-negative
            'order': order.upper() if order.upper() in ['ASC', 'DESC'] else 'DESC'
        }
        
        # Request body
        payload = {}
        
        if session_id:
            payload['sessionID'] = session_id
            
        if environment_id:
            payload['environmentID'] = environment_id
            
        if start_date:
            payload['startDate'] = start_date
            
        if end_date:
            payload['endDate'] = end_date
            
        if filters:
            payload['filters'] = filters[:50]  # Max 50 filters according to API spec
        
        try:
            response = requests.post(url, json=payload, params=params, headers=self._get_headers())
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Transcripts opgehaald: {len(data.get('transcripts', []))} gevonden")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Fout bij ophalen project transcripts: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text}")
            raise
    
    def get_transcripts_with_pagination(self, 
                                      batch_size: int = 25,
                                      max_transcripts: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Haal alle transcripts op met automatische paginering
        
        Args:
            batch_size: Aantal transcripts per batch (1-100)
            max_transcripts: Maximum aantal transcripts om op te halen (None = alle)
            
        Returns:
            List van alle transcript data
        """
        all_transcripts = []
        skip = 0
        
        while True:
            try:
                response = self.get_all_project_transcripts(
                    take=batch_size,
                    skip=skip,
                    order="DESC"
                )
                
                transcripts = response.get('transcripts', [])
                
                if not transcripts:
                    break
                
                all_transcripts.extend(transcripts)
                logger.info(f"Batch opgehaald: {len(transcripts)} transcripts (totaal: {len(all_transcripts)})")
                
                # Check if we've reached the maximum
                if max_transcripts and len(all_transcripts) >= max_transcripts:
                    all_transcripts = all_transcripts[:max_transcripts]
                    break
                
                # If we got fewer transcripts than requested, we've reached the end
                if len(transcripts) < batch_size:
                    break
                
                skip += batch_size
                
            except Exception as e:
                logger.error(f"Fout bij paginering: {e}")
                break
        
        logger.info(f"Totaal transcripts opgehaald: {len(all_transcripts)}")
        return all_transcripts
    
    def get_transcripts_by_date_range(self, 
                                    start_date: str, 
                                    end_date: str,
                                    batch_size: int = 25) -> List[Dict[str, Any]]:
        """
        Haal transcripts op binnen een specifieke datum range
        
        Args:
            start_date: Start datum (ISO format)
            end_date: Eind datum (ISO format)
            batch_size: Aantal transcripts per batch
            
        Returns:
            List van transcript data binnen de datum range
        """
        all_transcripts = []
        skip = 0
        
        # Ensure proper ISO format with timezone
        if not start_date.endswith('Z'):
            start_date = start_date.replace('+00:00', 'Z')
        if not end_date.endswith('Z'):
            end_date = end_date.replace('+00:00', 'Z')
        
        while True:
            try:
                response = self.get_all_project_transcripts(
                    take=batch_size,
                    skip=skip,
                    order="DESC",
                    start_date=start_date,
                    end_date=end_date
                )
                
                transcripts = response.get('transcripts', [])
                
                if not transcripts:
                    break
                
                all_transcripts.extend(transcripts)
                logger.info(f"Batch opgehaald: {len(transcripts)} transcripts (totaal: {len(all_transcripts)})")
                
                # If we got fewer transcripts than requested, we've reached the end
                if len(transcripts) < batch_size:
                    break
                
                skip += batch_size
                
            except Exception as e:
                logger.error(f"Fout bij ophalen transcripts per datum: {e}")
                break
        
        logger.info(f"Transcripts opgehaald voor periode {start_date} - {end_date}: {len(all_transcripts)}")
        return all_transcripts
    
    def analyze_transcript_properties(self, transcripts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyseer properties van transcripts
        
        Args:
            transcripts: List van transcript data
            
        Returns:
            Dict met analyse resultaten
        """
        analysis = {
            'total_transcripts': len(transcripts),
            'properties_analysis': {},
            'evaluations_analysis': {},
            'recording_analysis': {},
            'session_analysis': {}
        }
        
        for transcript in transcripts:
            # Analyze properties
            properties = transcript.get('properties', [])
            for prop in properties:
                prop_name = prop.get('name', 'unknown')
                prop_type = prop.get('type', 'unknown')
                prop_value = prop.get('value', '')
                
                if prop_name not in analysis['properties_analysis']:
                    analysis['properties_analysis'][prop_name] = {
                        'count': 0,
                        'values': [],
                        'type': prop_type
                    }
                
                analysis['properties_analysis'][prop_name]['count'] += 1
                if prop_value not in analysis['properties_analysis'][prop_name]['values']:
                    analysis['properties_analysis'][prop_name]['values'].append(prop_value)
            
            # Analyze evaluations
            evaluations = transcript.get('evaluations', [])
            for eval_item in evaluations:
                eval_name = eval_item.get('name', 'unknown')
                eval_type = eval_item.get('type', 'unknown')
                eval_value = eval_item.get('value', '')
                
                if eval_name not in analysis['evaluations_analysis']:
                    analysis['evaluations_analysis'][eval_name] = {
                        'count': 0,
                        'type': eval_type,
                        'values': []
                    }
                
                analysis['evaluations_analysis'][eval_name]['count'] += 1
                if eval_value not in analysis['evaluations_analysis'][eval_name]['values']:
                    analysis['evaluations_analysis'][eval_name]['values'].append(eval_value)
            
            # Analyze recordings
            recording_url = transcript.get('recordingURL')
            if recording_url:
                analysis['recording_analysis']['with_recording'] = analysis['recording_analysis'].get('with_recording', 0) + 1
            else:
                analysis['recording_analysis']['without_recording'] = analysis['recording_analysis'].get('without_recording', 0) + 1
            
            # Analyze sessions
            session_id = transcript.get('sessionID', '')
            if session_id:
                analysis['session_analysis']['unique_sessions'] = analysis['session_analysis'].get('unique_sessions', set())
                analysis['session_analysis']['unique_sessions'].add(session_id)
        
        # Convert set to count
        if 'unique_sessions' in analysis['session_analysis']:
            analysis['session_analysis']['unique_session_count'] = len(analysis['session_analysis']['unique_sessions'])
            del analysis['session_analysis']['unique_sessions']
        
        return analysis

    def fetch_all_transcripts_paginated(self, 
                                      project_id: str = None,
                                      batch_size: int = 100,
                                      **kwargs) -> List[Dict[str, Any]]:
        """
        Haal alle transcripts op met paginering (alternatieve methode)
        
        Args:
            project_id: Project ID (gebruikt self.project_id als None)
            batch_size: Aantal transcripts per batch (max 100)
            **kwargs: Extra parameters voor get_all_project_transcripts
            
        Returns:
            List van alle transcript data
        """
        if project_id is None:
            project_id = self.project_id
            
        all_transcripts = []
        skip = 0
        
        while True:
            try:
                response = self.get_all_project_transcripts(
                    take=batch_size,
                    skip=skip,
                    **kwargs
                )
                
                transcripts = response.get('transcripts', [])
                if not transcripts:
                    break
                    
                all_transcripts.extend(transcripts)
                logger.info(f"Batch opgehaald: {len(transcripts)} transcripts (totaal: {len(all_transcripts)})")
                
                # If we got fewer transcripts than requested, we've reached the end
                if len(transcripts) < batch_size:
                    break
                    
                skip += batch_size
                
            except Exception as e:
                logger.error(f"Fout bij paginering: {e}")
                break
        
        logger.info(f"Totaal transcripts opgehaald: {len(all_transcripts)}")
        return all_transcripts
    
    def export_to_json(self, data: Dict[str, Any], filename: str):
        """Export data naar JSON bestand"""
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"Data geëxporteerd naar {filename}")
        except Exception as e:
            logger.error(f"Fout bij exporteren naar JSON: {e}")
            raise
    
    def get_complete_project_data(self, 
                                project_id: str = None,
                                batch_size: int = 100,
                                export_filename: str = None) -> Dict[str, Any]:
        """
        Haal alle project data op inclusief evaluaties en transcripts
        
        Args:
            project_id: Project ID (gebruikt self.project_id als None)
            batch_size: Aantal transcripts per batch
            export_filename: Optionele bestandsnaam voor export
            
        Returns:
            Dict met complete project data
        """
        if project_id is None:
            project_id = self.project_id
            
        try:
            # Haal evaluaties op
            logger.info("Ophalen van evaluatie definities...")
            evaluations = self.get_all_evaluations(project_id)
            evaluation_count = len(evaluations.get("evaluations", []))
            logger.info(f"Gevonden: {evaluation_count} evaluaties")
            
            # Haal alle transcripts op
            logger.info("Ophalen van alle transcripts...")
            all_transcripts = self.fetch_all_transcripts_paginated(
                project_id=project_id,
                batch_size=batch_size
            )
            logger.info(f"Gevonden: {len(all_transcripts)} transcripts")
            
            # Combineer data
            combined_data = {
                "project_id": project_id,
                "fetched_at": datetime.now().isoformat(),
                "evaluations": evaluations.get("evaluations", []),
                "transcripts": all_transcripts,
                "summary": {
                    "total_transcripts": len(all_transcripts),
                    "total_evaluations": evaluation_count
                }
            }
            
            # Export naar JSON als bestandsnaam is opgegeven
            if export_filename:
                self.export_to_json(combined_data, export_filename)
            
            # Print samenvatting
            logger.info("=== Samenvatting ===")
            logger.info(f"Totaal transcripts: {len(all_transcripts)}")
            logger.info(f"Totaal evaluaties: {evaluation_count}")
            
            # Toon evaluatie resultaten van transcripts
            evaluation_results = []
            for transcript in all_transcripts:
                for evaluation in transcript.get("evaluations", []):
                    evaluation_results.append({
                        "transcript_id": transcript["id"],
                        "evaluation_name": evaluation["name"],
                        "evaluation_value": evaluation["value"],
                        "evaluation_cost": evaluation.get("cost", 0)
                    })
            
            logger.info(f"Totaal evaluatie resultaten: {len(evaluation_results)}")
            
            # Voeg evaluatie resultaten toe aan combined data
            combined_data["evaluation_results"] = evaluation_results
            combined_data["summary"]["total_evaluation_results"] = len(evaluation_results)
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Fout bij ophalen complete project data: {e}")
            raise

if __name__ == "__main__":
    # Test de analytics
    analytics = AIBotAnalytics()
    
    # Setup evaluaties
    print("Setting up evaluaties...")
    evaluations = analytics.setup_course_analysis_evaluations()
    print(f"Evaluaties aangemaakt: {evaluations}")
    
    # Analyseer conversaties
    print("Analyseren van conversaties...")
    results = analytics.analyze_conversations(days_back=7)
    print(f"Analyse voltooid: {results['total_transcripts']} transcripts geanalyseerd") 