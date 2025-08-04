import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
from voiceflow_analytics import VoiceflowAnalytics
from database import AnalyticsDatabase

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotAnalyzer:
    """
    Hybride chatbot analyzer die snelle chat combineert met Crew analyse
    """
    
    def __init__(self):
        self.analytics = VoiceflowAnalytics()
        self.database = AnalyticsDatabase()
        
        # Keywords die Crew analyse triggeren
        self.analysis_keywords = [
            'analyseer', 'rapport', 'kpi', 'advies', 'marketing', 
            'populair', 'cursus', 'conversie', 'trend', 'insight',
            'statistiek', 'data', 'overzicht', 'resultaat'
        ]
    
    def is_analysis_request(self, message: str) -> bool:
        """
        Bepaal of het bericht een analyse request is
        
        Args:
            message: Het gebruikers bericht
        
        Returns:
            True als het een analyse request is
        """
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.analysis_keywords)
    
    def get_quick_response(self, message: str) -> str:
        """
        Geef een snelle response voor normale chat
        
        Args:
            message: Het gebruikers bericht
        
        Returns:
            Snelle response
        """
        # Simpele keyword matching voor snelle responses
        message_lower = message.lower()
        
        if 'hallo' in message_lower or 'hoi' in message_lower:
            return "Hallo! Ik ben je Voiceflow Analytics assistent. Hoe kan ik je helpen?"
        
        elif 'help' in message_lower or 'help' in message_lower:
            return """
            Ik kan je helpen met:
            - Snelle vragen over Voiceflow
            - Analytics en rapporten (gebruik 'analyseer' of 'rapport')
            - Marketing insights (gebruik 'kpi' of 'advies')
            - Cursus populariteit (gebruik 'populair' of 'cursus')
            
            Wat wil je weten?
            """
        
        elif 'voiceflow' in message_lower:
            return "Voiceflow is een platform voor het bouwen van chatbots en conversational AI. Ik help je met analytics en insights!"
        
        else:
            return "Ik begrijp je vraag. Voor gedetailleerde analytics, gebruik woorden zoals 'analyseer', 'rapport', of 'kpi'."
    
    def get_analysis_response(self, message: str, days_back: int = 30) -> str:
        """
        Voer Crew analyse uit en geef gedetailleerde response
        
        Args:
            message: Het gebruikers bericht
            days_back: Aantal dagen terug om te analyseren
        
        Returns:
            Gedetailleerde analyse response
        """
        try:
            # Haal analytics data op
            summary = self.database.get_analytics_summary(days_back)
            
            # Bepaal type analyse op basis van keywords
            message_lower = message.lower()
            
            if 'cursus' in message_lower or 'populair' in message_lower:
                return self._analyze_popular_courses(summary)
            
            elif 'vraag' in message_lower or 'gesteld' in message_lower:
                return self._analyze_common_questions(summary)
            
            elif 'conversie' in message_lower or 'kpi' in message_lower:
                return self._analyze_conversion_rates(summary)
            
            elif 'marketing' in message_lower or 'advies' in message_lower:
                return self._analyze_marketing_insights(summary)
            
            else:
                return self._analyze_general_overview(summary)
                
        except Exception as e:
            logger.error(f"Fout bij analyse: {e}")
            return f"Sorry, er is een fout opgetreden bij de analyse: {str(e)}"
    
    def _analyze_popular_courses(self, summary: Dict[str, Any]) -> str:
        """Analyseer populaire cursussen"""
        courses = summary['popular_courses']
        
        if not courses:
            return "📊 **Cursus Analyse**\n\nNog geen cursus data beschikbaar. Start een analyse om inzichten te krijgen."
        
        response = "📊 **Populairste Cursussen**\n\n"
        
        for i, course in enumerate(courses[:5], 1):
            response += f"{i}. **{course['course_name']}** - {course['mentions']} mentions\n"
        
        if len(courses) > 5:
            response += f"\n... en nog {len(courses) - 5} andere cursussen"
        
        response += f"\n\n💡 **Insight**: {courses[0]['course_name']} is momenteel het meest populair!"
        
        return response
    
    def _analyze_common_questions(self, summary: Dict[str, Any]) -> str:
        """Analyseer meest gestelde vragen"""
        questions = summary['common_questions']
        
        if not questions:
            return "❓ **Vraag Analyse**\n\nNog geen vraag analyse beschikbaar. Start een analyse om inzichten te krijgen."
        
        response = "❓ **Meest Gestelde Vragen**\n\n"
        
        for i, question in enumerate(questions[:5], 1):
            response += f"{i}. **{question['question_type']}** - {question['count']} keer\n"
        
        response += "\n💡 **Tip**: Focus je content op deze vraagtypes voor betere conversie!"
        
        return response
    
    def _analyze_conversion_rates(self, summary: Dict[str, Any]) -> str:
        """Analyseer conversie rates"""
        conversion = summary['conversion_rates']
        
        response = "📈 **Conversie Analyse**\n\n"
        response += f"• **Totaal gesprekken**: {conversion['total_conversations']}\n"
        response += f"• **Succesvolle conversies**: {conversion['successful_conversions']}\n"
        response += f"• **Conversie rate**: {conversion['conversion_rate']:.1f}%\n\n"
        
        if conversion['conversion_rate'] > 20:
            response += "🎉 **Excellent!** Je conversie rate is erg goed!"
        elif conversion['conversion_rate'] > 10:
            response += "👍 **Goed!** Je conversie rate is redelijk."
        else:
            response += "⚠️ **Verbetering nodig!** Focus op het verhogen van je conversie rate."
        
        return response
    
    def _analyze_marketing_insights(self, summary: Dict[str, Any]) -> str:
        """Geef marketing insights"""
        courses = summary['popular_courses']
        conversion = summary['conversion_rates']
        
        response = "🎯 **Marketing Insights**\n\n"
        
        if courses:
            top_course = courses[0]
            response += f"**Top Cursus**: {top_course['course_name']} ({top_course['mentions']} mentions)\n"
            response += f"**Conversie Rate**: {conversion['conversion_rate']:.1f}%\n\n"
            
            response += "**Aanbevelingen**:\n"
            response += "1. Promoot je populairste cursus meer\n"
            response += "2. Analyseer waarom andere cursussen minder populair zijn\n"
            response += "3. Verbeter je conversie rate door A/B testing\n"
            response += "4. Focus op de meest gestelde vragen in je content\n"
        
        else:
            response += "Nog geen data beschikbaar. Start een analyse voor marketing insights!"
        
        return response
    
    def _analyze_general_overview(self, summary: Dict[str, Any]) -> str:
        """Geef algemeen overzicht"""
        conversion = summary['conversion_rates']
        courses = summary['popular_courses']
        
        response = "📊 **Algemeen Overzicht**\n\n"
        response += f"• **Totaal gesprekken**: {conversion['total_conversations']}\n"
        response += f"• **Conversie rate**: {conversion['conversion_rate']:.1f}%\n"
        response += f"• **Unieke cursussen**: {len(courses)}\n\n"
        
        if courses:
            response += f"**Populairste cursus**: {courses[0]['course_name']}\n"
        
        response += "\n💡 **Tip**: Gebruik 'cursus', 'vraag', of 'conversie' voor specifieke analyses!"
        
        return response
    
    def process_message(self, message: str, user_id: str = None) -> str:
        """
        Verwerk een bericht en geef gepaste response
        
        Args:
            message: Het gebruikers bericht
            user_id: Optionele user ID voor logging
        
        Returns:
            Response bericht
        """
        # Log het bericht
        if user_id:
            self.database.store_conversation_log({
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                'request_type': 'text',
                'response_text': message,
                'project_id': self.analytics.project_id
            })
        
        # Bepaal of het een analyse request is
        if self.is_analysis_request(message):
            logger.info(f"Analysis request gedetecteerd: {message}")
            return self.get_analysis_response(message)
        else:
            return self.get_quick_response(message)
    
    def run_analysis(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Voer een volledige analyse uit
        
        Args:
            days_back: Aantal dagen terug om te analyseren
        
        Returns:
            Analyse resultaten
        """
        try:
            # Voer Voiceflow analyse uit
            results = self.analytics.analyze_conversations(days_back)
            
            # Sla resultaten op in database
            for eval_result in results.get('evaluation_results', []):
                self.database.store_evaluation_result(eval_result)
            
            logger.info(f"Analyse voltooid: {results['total_transcripts']} transcripts geanalyseerd")
            return results
            
        except Exception as e:
            logger.error(f"Fout bij uitvoeren analyse: {e}")
            raise

# Test functie
def test_chatbot():
    """Test de chatbot analyzer"""
    analyzer = ChatbotAnalyzer()
    
    # Test snelle chat
    print("=== Snelle Chat Test ===")
    print(analyzer.process_message("Hallo"))
    print(analyzer.process_message("Wat is Voiceflow?"))
    
    # Test analyse requests
    print("\n=== Analyse Test ===")
    print(analyzer.process_message("Analyseer de populairste cursussen"))
    print(analyzer.process_message("Geef me een marketing rapport"))
    print(analyzer.process_message("Wat zijn de KPI's?"))

if __name__ == "__main__":
    test_chatbot() 