#!/usr/bin/env python3
"""
Test script voor enhanced evaluation results functionaliteit
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from voiceflow_analytics import VoiceflowAnalytics

# Load environment variables
load_dotenv()

def test_enhanced_evaluation_analysis():
    """Test de enhanced evaluation analysis functionaliteit"""
    print("🧪 Test Enhanced Evaluation Analysis")
    print("="*60)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Haal complete project data op
        print("📊 Ophalen van complete project data...")
        complete_data = analytics.get_complete_project_data(
            batch_size=50,
            export_filename="test_enhanced_evaluations.json"
        )
        
        if not complete_data:
            print("❌ Geen data opgehaald")
            return False
        
        evaluation_results = complete_data.get('evaluation_results', [])
        print(f"✅ {len(evaluation_results)} evaluation resultaten gevonden")
        
        # Test de enhanced analysis functies
        from voiceflow_dashboard import create_detailed_evaluation_analysis, show_enhanced_evaluation_results
        
        # Maak een dummy df_evaluations voor testing
        import pandas as pd
        evaluations = complete_data.get('evaluations', [])
        df_evaluations = pd.DataFrame(evaluations)
        
        # Test create_detailed_evaluation_analysis
        print("\n🔍 Test create_detailed_evaluation_analysis...")
        eval_analysis = create_detailed_evaluation_analysis(evaluation_results, df_evaluations)
        
        if eval_analysis:
            print(f"✅ Evaluation analysis gemaakt voor {len(eval_analysis)} evaluaties")
            
            # Toon details per evaluatie
            for eval_name, data in eval_analysis.items():
                print(f"\n📋 {eval_name}:")
                print(f"  Type: {data['type']}")
                print(f"  Total Runs: {data['total_runs']}")
                print(f"  Total Cost: ${data['total_cost']:.4f}")
                print(f"  Avg Cost: ${data['avg_cost']:.4f}")
                
                if data['success_rate'] is not None:
                    print(f"  Success Rate: {data['success_rate']:.1f}%")
                
                if data['avg_rating'] is not None:
                    print(f"  Avg Rating: {data['avg_rating']:.2f}")
                
                print(f"  Unique Values: {len(data['value_distribution'])}")
                
                # Toon value distribution
                if data['value_distribution']:
                    print("  Value Distribution:")
                    for value, count in data['value_distribution'].items():
                        print(f"    {value}: {count} keer")
        else:
            print("❌ Evaluation analysis gefaald")
            return False
        
        # Test summary statistieken
        print("\n📊 Summary Statistieken:")
        total_runs = sum(data['total_runs'] for data in eval_analysis.values())
        total_cost = sum(data['total_cost'] for data in eval_analysis.values())
        avg_cost_per_run = total_cost / total_runs if total_runs > 0 else 0
        
        print(f"  Total Runs: {total_runs}")
        print(f"  Total Cost: ${total_cost:.4f}")
        print(f"  Avg Cost per Run: ${avg_cost_per_run:.4f}")
        
        # Test type-specifieke analyses
        print("\n🎯 Type-specifieke Analyses:")
        for eval_name, data in eval_analysis.items():
            if data['type'] == 'boolean':
                print(f"  {eval_name} (Boolean): Success Rate = {data['success_rate']:.1f}%")
            elif data['type'] == 'number':
                print(f"  {eval_name} (Number): Avg Rating = {data['avg_rating']:.2f}")
            elif data['type'] == 'string':
                print(f"  {eval_name} (String): {len(data['values'])} responses")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def test_evaluation_details():
    """Test de evaluation details functionaliteit"""
    print("\n🧪 Test Evaluation Details")
    print("="*50)
    
    try:
        analytics = VoiceflowAnalytics()
        
        # Haal data op
        complete_data = analytics.get_complete_project_data(batch_size=25)
        evaluation_results = complete_data.get('evaluation_results', [])
        
        if not evaluation_results:
            print("❌ Geen evaluation resultaten gevonden")
            return False
        
        # Test show_evaluation_details functie
        from voiceflow_dashboard import create_detailed_evaluation_analysis, show_evaluation_details
        
        import pandas as pd
        evaluations = complete_data.get('evaluations', [])
        df_evaluations = pd.DataFrame(evaluations)
        
        eval_analysis = create_detailed_evaluation_analysis(evaluation_results, df_evaluations)
        
        if eval_analysis:
            # Test voor eerste evaluatie
            first_eval_name = list(eval_analysis.keys())[0]
            first_eval_data = eval_analysis[first_eval_name]
            
            print(f"✅ Testing details voor: {first_eval_name}")
            print(f"  Type: {first_eval_data['type']}")
            print(f"  Total Runs: {first_eval_data['total_runs']}")
            print(f"  Total Cost: ${first_eval_data['total_cost']:.4f}")
            print(f"  Avg Cost: ${first_eval_data['avg_cost']:.4f}")
            
            # Test value distribution
            if first_eval_data['value_distribution']:
                print(f"  Value Distribution: {len(first_eval_data['value_distribution'])} unique values")
                for value, count in list(first_eval_data['value_distribution'].items())[:5]:
                    print(f"    {value}: {count} keer")
            
            # Test recent results
            if first_eval_data['values']:
                recent_count = min(10, len(first_eval_data['values']))
                print(f"  Recent Results: {recent_count} laatste resultaten")
        
        return True
        
    except Exception as e:
        print(f"❌ Fout: {e}")
        return False

def main():
    """Hoofdfunctie"""
    print("🚀 Enhanced Evaluation Results Test Suite")
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
    
    # Run tests
    tests = [
        ("Enhanced Evaluation Analysis", test_enhanced_evaluation_analysis),
        ("Evaluation Details", test_evaluation_details)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Onverwachte fout in {test_name}: {e}")
            results.append((test_name, False))
    
    # Toon resultaten
    print("\n" + "="*60)
    print("📊 Test Resultaten:")
    print("="*60)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if success:
            passed += 1
    
    print(f"\nTotaal: {passed}/{len(results)} tests geslaagd")
    
    if passed == len(results):
        print("🎉 Alle tests geslaagd! Enhanced evaluation results werken correct.")
    else:
        print("⚠️  Sommige tests gefaald. Controleer de implementatie.")

if __name__ == "__main__":
    main() 