import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AnalyticsDatabase:
    """
    Database handler voor Voiceflow analytics data
    """
    
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase configuratie ontbreekt, gebruik lokale JSON storage")
            self.use_local_storage = True
            self.local_data_file = "analytics_data.json"
        else:
            self.use_local_storage = False
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
    
    def _load_local_data(self) -> Dict[str, Any]:
        """Laad data uit lokale JSON file"""
        try:
            with open(self.local_data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'conversations': [],
                'evaluations': [],
                'course_mentions': [],
                'question_analysis': [],
                'conversion_data': []
            }
    
    def _save_local_data(self, data: Dict[str, Any]):
        """Sla data op in lokale JSON file"""
        with open(self.local_data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def store_conversation_log(self, conversation_data: Dict[str, Any]):
        """
        Sla een conversatie log op
        
        Args:
            conversation_data: Dict met conversatie data
        """
        if self.use_local_storage:
            data = self._load_local_data()
            data['conversations'].append({
                **conversation_data,
                'stored_at': datetime.now().isoformat()
            })
            self._save_local_data(data)
        else:
            try:
                self.supabase.table('conversation_logs').insert({
                    'user_id': conversation_data.get('user_id'),
                    'timestamp': conversation_data.get('timestamp'),
                    'request_type': conversation_data.get('request_type'),
                    'response_text': conversation_data.get('response_text'),
                    'course_mentioned': conversation_data.get('course_mentioned'),
                    'project_id': conversation_data.get('project_id'),
                    'transcript_id': conversation_data.get('transcript_id'),
                    'raw_data': json.dumps(conversation_data.get('raw_data', {}))
                }).execute()
            except Exception as e:
                logger.error(f"Fout bij opslaan conversatie log: {e}")
    
    def store_evaluation_result(self, evaluation_data: Dict[str, Any]):
        """
        Sla een evaluatie resultaat op
        
        Args:
            evaluation_data: Dict met evaluatie data
        """
        if self.use_local_storage:
            data = self._load_local_data()
            data['evaluations'].append({
                **evaluation_data,
                'stored_at': datetime.now().isoformat()
            })
            self._save_local_data(data)
        else:
            try:
                self.supabase.table('evaluation_results').insert({
                    'transcript_id': evaluation_data.get('transcript_id'),
                    'evaluation_id': evaluation_data.get('evaluation_id'),
                    'evaluation_name': evaluation_data.get('evaluation_name'),
                    'result': json.dumps(evaluation_data.get('result', {})),
                    'project_id': evaluation_data.get('project_id'),
                    'created_at': datetime.now().isoformat()
                }).execute()
            except Exception as e:
                logger.error(f"Fout bij opslaan evaluatie resultaat: {e}")
    
    def get_popular_courses(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Haal populairste cursussen op
        
        Args:
            days_back: Aantal dagen terug om te analyseren
        
        Returns:
            List van cursussen met mention counts
        """
        if self.use_local_storage:
            data = self._load_local_data()
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Filter recente conversaties
            recent_conversations = [
                conv for conv in data['conversations']
                if datetime.fromisoformat(conv.get('timestamp', '')) > cutoff_date
            ]
            
            # Tel cursus mentions
            course_counts = {}
            for conv in recent_conversations:
                course = conv.get('course_mentioned')
                if course:
                    course_counts[course] = course_counts.get(course, 0) + 1
            
            return [
                {'course_name': course, 'mentions': count}
                for course, count in sorted(course_counts.items(), key=lambda x: x[1], reverse=True)
            ]
        else:
            try:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                response = self.supabase.table('conversation_logs').select(
                    'course_mentioned'
                ).gte('timestamp', cutoff_date.isoformat()).execute()
                
                # Tel mentions
                course_counts = {}
                for row in response.data:
                    course = row.get('course_mentioned')
                    if course:
                        course_counts[course] = course_counts.get(course, 0) + 1
                
                return [
                    {'course_name': course, 'mentions': count}
                    for course, count in sorted(course_counts.items(), key=lambda x: x[1], reverse=True)
                ]
            except Exception as e:
                logger.error(f"Fout bij ophalen populaire cursussen: {e}")
                return []
    
    def get_common_questions(self, days_back: int = 30) -> List[Dict[str, Any]]:
        """
        Haal meest gestelde vragen op
        
        Args:
            days_back: Aantal dagen terug om te analyseren
        
        Returns:
            List van vragen met counts
        """
        if self.use_local_storage:
            data = self._load_local_data()
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Filter recente evaluaties
            recent_evaluations = [
                eval_data for eval_data in data['evaluations']
                if datetime.fromisoformat(eval_data.get('stored_at', '')) > cutoff_date
                and eval_data.get('evaluation_name') == 'Meest Gestelde Vragen'
            ]
            
            # Analyseer resultaten
            question_counts = {}
            for eval_data in recent_evaluations:
                result = eval_data.get('result', {})
                # Hier zou je de AI resultaten moeten parsen
                # Voor nu gebruiken we een simpele aanpak
                if 'questions' in str(result):
                    question_counts['algemene vragen'] = question_counts.get('algemene vragen', 0) + 1
            
            return [
                {'question_type': q_type, 'count': count}
                for q_type, count in sorted(question_counts.items(), key=lambda x: x[1], reverse=True)
            ]
        else:
            try:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                response = self.supabase.table('evaluation_results').select(
                    'result'
                ).eq('evaluation_name', 'Meest Gestelde Vragen').gte('created_at', cutoff_date.isoformat()).execute()
                
                # Analyseer resultaten
                question_counts = {}
                for row in response.data:
                    result = json.loads(row.get('result', '{}'))
                    # Hier zou je de AI resultaten moeten parsen
                    if 'questions' in str(result):
                        question_counts['algemene vragen'] = question_counts.get('algemene vragen', 0) + 1
                
                return [
                    {'question_type': q_type, 'count': count}
                    for q_type, count in sorted(question_counts.items(), key=lambda x: x[1], reverse=True)
                ]
            except Exception as e:
                logger.error(f"Fout bij ophalen veelgestelde vragen: {e}")
                return []
    
    def get_conversion_rates(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Haal conversie rates op
        
        Args:
            days_back: Aantal dagen terug om te analyseren
        
        Returns:
            Dict met conversie statistieken
        """
        if self.use_local_storage:
            data = self._load_local_data()
            cutoff_date = datetime.now() - timedelta(days=days_back)
            
            # Filter recente evaluaties
            recent_evaluations = [
                eval_data for eval_data in data['evaluations']
                if datetime.fromisoformat(eval_data.get('stored_at', '')) > cutoff_date
                and eval_data.get('evaluation_name') == 'Conversie Analyse'
            ]
            
            total_conversations = len(recent_evaluations)
            successful_conversions = sum(
                1 for eval_data in recent_evaluations
                if 'inschrijving' in str(eval_data.get('result', '')).lower()
            )
            
            return {
                'total_conversations': total_conversations,
                'successful_conversions': successful_conversions,
                'conversion_rate': (successful_conversions / total_conversations * 100) if total_conversations > 0 else 0
            }
        else:
            try:
                cutoff_date = datetime.now() - timedelta(days=days_back)
                response = self.supabase.table('evaluation_results').select(
                    'result'
                ).eq('evaluation_name', 'Conversie Analyse').gte('created_at', cutoff_date.isoformat()).execute()
                
                total_conversations = len(response.data)
                successful_conversions = sum(
                    1 for row in response.data
                    if 'inschrijving' in str(json.loads(row.get('result', '{}'))).lower()
                )
                
                return {
                    'total_conversations': total_conversations,
                    'successful_conversions': successful_conversions,
                    'conversion_rate': (successful_conversions / total_conversations * 100) if total_conversations > 0 else 0
                }
            except Exception as e:
                logger.error(f"Fout bij ophalen conversie rates: {e}")
                return {
                    'total_conversations': 0,
                    'successful_conversions': 0,
                    'conversion_rate': 0
                }
    
    def get_analytics_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Haal een complete analytics samenvatting op
        
        Args:
            days_back: Aantal dagen terug om te analyseren
        
        Returns:
            Dict met alle analytics data
        """
        return {
            'popular_courses': self.get_popular_courses(days_back),
            'common_questions': self.get_common_questions(days_back),
            'conversion_rates': self.get_conversion_rates(days_back),
            'analysis_period_days': days_back,
            'last_updated': datetime.now().isoformat()
        }

if __name__ == "__main__":
    # Test de database
    db = AnalyticsDatabase()
    
    # Test data opslaan
    test_conversation = {
        'user_id': 'test_user_123',
        'timestamp': datetime.now().isoformat(),
        'request_type': 'text',
        'response_text': 'Ik wil meer weten over de AI cursus',
        'course_mentioned': 'AI cursus',
        'project_id': 'test_project',
        'transcript_id': 'test_transcript_123'
    }
    
    db.store_conversation_log(test_conversation)
    print("Test conversatie opgeslagen")
    
    # Test analytics ophalen
    summary = db.get_analytics_summary(days_back=7)
    print(f"Analytics samenvatting: {summary}") 