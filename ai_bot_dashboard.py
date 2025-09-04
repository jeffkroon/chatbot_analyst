#!/usr/bin/env python3
"""
Voiceflow Analytics Dashboard - Alleen echte data uit de API
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv
from ai_bot_analytics import AIBotAnalytics
import requests # Added for debug information

# Load environment variables
load_dotenv()

# ===== API FUNCTIES =====
def get_real_voiceflow_data():
    """Haal echte data op van AI Bot API"""
    try:
        analytics = AIBotAnalytics()
        
        # Haal complete project data op
        complete_data = analytics.get_complete_project_data(
            batch_size=100,
            export_filename="dashboard_data.json"
        )
        
        return complete_data
        
    except Exception as e:
        st.error(f"Fout bij ophalen AI Bot data: {e}")
        return None

def get_evaluations_data():
    """Haal evaluaties op van AI Bot API"""
    try:
        analytics = AIBotAnalytics()
        evaluations = analytics.get_all_evaluations()
        return evaluations.get('evaluations', [])
        
    except Exception as e:
        st.error(f"Fout bij ophalen evaluaties: {e}")
        return []

def get_transcripts_data():
    """Haal transcripts op van AI Bot API"""
    try:
        analytics = AIBotAnalytics()
        transcripts = analytics.get_transcripts_with_pagination(
            batch_size=100
        )
        return transcripts
        
    except Exception as e:
        st.error(f"Fout bij ophalen transcripts: {e}")
        return []

# ===== DATA PROCESSING =====
def process_transcript_data(transcripts):
    """Verwerk transcript data voor dashboard"""
    if not transcripts:
        return pd.DataFrame()
    
    processed_data = []
    
    for transcript in transcripts:
        # Extract basic info
        transcript_data = {
            'transcript_id': transcript.get('id', 'Unknown'),
            'session_id': transcript.get('sessionID', 'Unknown'),
            'created_at': transcript.get('createdAt', datetime.now()),
            'properties_count': len(transcript.get('properties', [])),
            'evaluations_count': len(transcript.get('evaluations', [])),
            'has_recording': bool(transcript.get('recordingURL')),
            'ended_at': transcript.get('endedAt'),
            'expires_at': transcript.get('expiresAt')
        }
        
        # Extract evaluation results
        evaluations = transcript.get('evaluations', [])
        for eval_item in evaluations:
            eval_name = eval_item.get('name', 'Unknown')
            eval_value = eval_item.get('value', '')
            eval_cost = eval_item.get('cost', 0)
            
            transcript_data[f'eval_{eval_name}_value'] = eval_value
            transcript_data[f'eval_{eval_name}_cost'] = eval_cost
        
        # Extract properties
        properties = transcript.get('properties', [])
        for prop in properties:
            prop_name = prop.get('name', 'Unknown')
            prop_value = prop.get('value', '')
            
            transcript_data[f'prop_{prop_name}'] = prop_value
        
        processed_data.append(transcript_data)
    
    df = pd.DataFrame(processed_data)
    
    # Convert timestamps
    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['date'] = df['created_at'].dt.date
        df['hour'] = df['created_at'].dt.hour
    
    return df

def process_evaluation_data(evaluations):
    """Verwerk evaluatie data voor dashboard"""
    if not evaluations:
        return pd.DataFrame()
    
    processed_data = []
    
    for eval_item in evaluations:
        eval_data = {
            'id': eval_item.get('id', 'Unknown'),
            'name': eval_item.get('name', 'Unknown'),
            'type': eval_item.get('type', 'Unknown'),
            'description': eval_item.get('description', ''),
            'enabled': eval_item.get('enabled', False),
            'default': eval_item.get('default', False)
        }
        
        processed_data.append(eval_data)
    
    return pd.DataFrame(processed_data)

# ===== ENHANCED EVALUATION RESULTS =====
def create_detailed_evaluation_analysis(evaluation_results, df_evaluations):
    """Create detailed analysis per evaluation"""
    if not evaluation_results:
        return None
    
    # Group results by evaluation name
    eval_analysis = {}
    
    for result in evaluation_results:
        eval_name = result['evaluation_name']
        eval_value = result['evaluation_value']
        transcript_id = result['transcript_id']
        
        if eval_name not in eval_analysis:
            eval_analysis[eval_name] = {
                'name': eval_name,
                'type': 'unknown',
                'total_runs': 0,
                'values': [],
                'transcripts': [],
                'value_distribution': {},
                'success_rate': None,
                'avg_rating': None
            }
        
        # Get evaluation type from evaluations data
        if not df_evaluations.empty:
            eval_info = df_evaluations[df_evaluations['name'] == eval_name]
            if not eval_info.empty:
                eval_analysis[eval_name]['type'] = eval_info.iloc[0]['type']
        
        # Add data
        eval_analysis[eval_name]['total_runs'] += 1
        eval_analysis[eval_name]['values'].append(eval_value)
        eval_analysis[eval_name]['transcripts'].append(transcript_id)
        
        # Count value distribution
        if eval_value in eval_analysis[eval_name]['value_distribution']:
            eval_analysis[eval_name]['value_distribution'][eval_value] += 1
        else:
            eval_analysis[eval_name]['value_distribution'][eval_value] = 1
    
    # Calculate statistics
    for eval_name, data in eval_analysis.items():
        # Calculate success rate for boolean evaluations
        if data['type'] == 'boolean':
            true_count = data['value_distribution'].get(True, 0) + data['value_distribution'].get('true', 0)
            data['success_rate'] = (true_count / data['total_runs']) * 100 if data['total_runs'] > 0 else 0
        
        # Calculate average rating for number evaluations
        elif data['type'] == 'number':
            numeric_values = [v for v in data['values'] if isinstance(v, (int, float))]
            data['avg_rating'] = sum(numeric_values) / len(numeric_values) if numeric_values else 0
    
    return eval_analysis

def show_evaluation_details(eval_name, eval_data):
    """Show detailed results for a specific evaluation"""
    st.write(f"**{eval_name}** ({eval_data['type']} evaluation)")
    
    # Metrics row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Runs", eval_data['total_runs'])
    
    with col2:
        if eval_data['success_rate'] is not None:
            st.metric("Success Rate", f"{eval_data['success_rate']:.1f}%")
        else:
            st.metric("Unique Values", len(eval_data['value_distribution']))
    
    with col3:
        if eval_data['avg_rating'] is not None:
            st.metric("Average Rating", f"{eval_data['avg_rating']:.2f}")
        else:
            st.metric("Most Common", max(eval_data['value_distribution'].items(), key=lambda x: x[1])[0] if eval_data['value_distribution'] else "N/A")
    
    # Value distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Value Distribution**")
        if eval_data['value_distribution']:
            # Create chart based on evaluation type
            values = list(eval_data['value_distribution'].keys())
            counts = list(eval_data['value_distribution'].values())
            
            if eval_data['type'] == 'boolean':
                # Pie chart for boolean
                fig = px.pie(
                    values=counts,
                    names=[str(v) for v in values],
                    title=f"Results Distribution - {eval_name}"
                )
            else:
                # Bar chart for others
                fig = px.bar(
                    x=[str(v) for v in values],
                    y=counts,
                    title=f"Results Distribution - {eval_name}",
                    labels={'x': 'Value', 'y': 'Count'}
                )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.write("**Recent Results**")
        # Show last 10 results
        recent_results = []
        for i, (value, transcript_id) in enumerate(zip(eval_data['values'][-10:], eval_data['transcripts'][-10:])):
            recent_results.append({
                'Value': str(value),
                'Transcript ID': transcript_id[:8] + '...' if len(transcript_id) > 8 else transcript_id
            })
        
        if recent_results:
            st.dataframe(pd.DataFrame(recent_results), use_container_width=True)
    
    # Detailed results table (expandable)
    with st.expander(f"All Results for {eval_name} ({len(eval_data['values'])} total)"):
        detailed_results = []
        for value, transcript_id in zip(eval_data['values'], eval_data['transcripts']):
            detailed_results.append({
                'Transcript ID': transcript_id,
                'Result Value': str(value),
                'Value Type': type(value).__name__
            })
        
        st.dataframe(pd.DataFrame(detailed_results), use_container_width=True)

def show_enhanced_evaluation_results(complete_data, df_evaluations):
    """Show enhanced evaluation results section"""
    st.header("📈 Detailed Evaluation Results")
    
    evaluation_results = complete_data.get('evaluation_results', [])
    if not evaluation_results:
        st.info("Geen evaluation resultaten beschikbaar")
        return
    
    # Create detailed analysis
    eval_analysis = create_detailed_evaluation_analysis(evaluation_results, df_evaluations)
    
    if not eval_analysis:
        st.info("Kon evaluation analyse niet maken")
        return
    
    # Overview metrics
    st.subheader("📊 Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Unique Evaluations", len(eval_analysis))
    
    with col2:
        total_runs = sum(data['total_runs'] for data in eval_analysis.values())
        st.metric("Total Evaluation Runs", total_runs)
    
    with col3:
        st.metric("Total Results", len(evaluation_results))
    
    # Detailed results per evaluation
    st.subheader("🔍 Results per Evaluation")
    
    # Create tabs for each evaluation
    eval_names = list(eval_analysis.keys())
    if len(eval_names) <= 5:
        tabs = st.tabs(eval_names)
        
        for i, (eval_name, tab) in enumerate(zip(eval_names, tabs)):
            with tab:
                show_evaluation_details(eval_name, eval_analysis[eval_name])
    else:
        # Use selectbox for many evaluations
        selected_eval = st.selectbox("Select Evaluation", eval_names)
        if selected_eval:
            show_evaluation_details(selected_eval, eval_analysis[selected_eval])
    
# ===== COURSE ANALYTICS =====
def analyze_course_choices(evaluation_results):
    """Analyseer welke cursussen het meest worden gekozen"""
    if not evaluation_results:
        return None
    
    # Filter voor AI course chosen evaluaties
    course_results = [result for result in evaluation_results if result['evaluation_name'] == 'AI course chosen']
    
    if not course_results:
        return None
    
    # Tel hoe vaak elke cursus wordt gekozen
    course_counts = {}
    course_details = []
    
    for result in course_results:
        course_name = result['evaluation_value']
        transcript_id = result['transcript_id']
        
        # Skip None, empty, or invalid course names - meer strikte filtering
        if (not course_name or 
            course_name == 'None' or 
            course_name == '' or 
            course_name is None or
            str(course_name).lower() == 'none' or
            str(course_name).strip() == ''):
            continue
        
        if course_name in course_counts:
            course_counts[course_name] += 1
        else:
            course_counts[course_name] = 1
        
        course_details.append({
            'course_name': course_name,
            'transcript_id': transcript_id,
            'chosen_at': datetime.now().isoformat()  # We hebben geen timestamp, dus gebruiken we nu
        })
    
    # Extra filter: verwijder alle cursussen met 0 counts (voor de zekerheid)
    course_counts = {k: v for k, v in course_counts.items() if v > 0}
    
    # Sorteer op populariteit
    sorted_courses = sorted(course_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'total_choices': len(course_details),  # Gebruik course_details in plaats van course_results
        'unique_courses': len(course_counts),
        'course_counts': course_counts,
        'sorted_courses': sorted_courses,
        'course_details': course_details
    }

def show_course_analytics(complete_data):
    """Toon gedetailleerde course analytics"""
    st.header("🎯 Course Analytics")
    
    evaluation_results = complete_data.get('evaluation_results', [])
    course_analysis = analyze_course_choices(evaluation_results)
    
    if not course_analysis or course_analysis['total_choices'] == 0:
        st.info("Geen geldige course keuze data beschikbaar")
        return
    
    # Overview metrics
    st.subheader("📊 Course Choice Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Course Choices", course_analysis['total_choices'])
    
    with col2:
        st.metric("Unique Courses", course_analysis['unique_courses'])
    
    with col3:
        most_popular = course_analysis['sorted_courses'][0] if course_analysis['sorted_courses'] else ('N/A', 0)
        st.metric("Most Popular Course", most_popular[0])
    
    with col4:
        if course_analysis['sorted_courses']:
            popularity_percentage = (most_popular[1] / course_analysis['total_choices']) * 100
            st.metric("Top Course Share", f"{popularity_percentage:.1f}%")
        else:
            st.metric("Top Course Share", "0%")
    
    # Course popularity chart
    st.subheader("📈 Course Popularity")
    
    if course_analysis['sorted_courses']:
        # Filter out any remaining None or invalid values
        valid_courses = [(name, count) for name, count in course_analysis['sorted_courses'] 
                         if name and name != 'None' and str(name).lower() != 'none' and str(name).strip() != '']
        
        if not valid_courses:
            st.info("Geen geldige cursus data beschikbaar voor visualisatie")
            return
        
        # Top 10 cursussen
        top_courses = valid_courses[:10]
        course_names = [course[0] for course in top_courses]
        course_counts = [course[1] for course in top_courses]
        
        # Maak een mooie bar chart
        fig = px.bar(
            x=course_counts,
            y=course_names,
            orientation='h',
            title="Top 10 Most Chosen Courses",
            labels={'x': 'Number of Choices', 'y': 'Course Name'},
            color=course_counts,
            color_continuous_scale='viridis'
        )
        
        # Verbeter de layout
        fig.update_layout(
            height=500,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Toon ook een pie chart voor de top 5
        if len(top_courses) >= 5:
            top_5_courses = top_courses[:5]
            other_choices = sum(course[1] for course in top_courses[5:])
            
            pie_data = {
                'Course': [course[0] for course in top_5_courses] + ['Others'],
                'Choices': [course[1] for course in top_5_courses] + [other_choices]
            }
            
            fig_pie = px.pie(
                pie_data,
                values='Choices',
                names='Course',
                title="Course Choice Distribution (Top 5 + Others)",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
    
    # Detailed course table
    st.subheader("📋 Detailed Course Analysis")
    
    # Maak een mooie tabel met alle cursussen (gebruik valid_courses)
    course_table_data = []
    for i, (course_name, count) in enumerate(valid_courses):
        percentage = (count / course_analysis['total_choices']) * 100
        course_table_data.append({
            'Rank': i + 1,
            'Course Name': course_name,
            'Times Chosen': count,
            'Percentage': f"{percentage:.1f}%",
            'Share': f"{count}/{course_analysis['total_choices']}"
        })
    
    # Toon de tabel met styling
    df_courses = pd.DataFrame(course_table_data)
    st.dataframe(
        df_courses,
        use_container_width=True,
        hide_index=True
    )
    
    # Course insights
    st.subheader("💡 Course Insights")
    
    if valid_courses:
        top_course = valid_courses[0]
        top_percentage = (top_course[1] / course_analysis['total_choices']) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏆 Most Popular Course:**")
            st.write(f"**{top_course[0]}** wordt het meest gekozen")
            st.write(f"- {top_course[1]} keer gekozen ({top_percentage:.1f}%)")
            st.write(f"- Dit is de favoriete cursus van de AI")
        
        with col2:
            st.write("**📊 Distribution Insights:**")
            if len(valid_courses) >= 3:
                top_3_total = sum(course[1] for course in valid_courses[:3])
                top_3_percentage = (top_3_total / course_analysis['total_choices']) * 100
                st.write(f"- Top 3 cursussen: {top_3_percentage:.1f}% van alle keuzes")
            
            st.write(f"- {course_analysis['unique_courses']} verschillende cursussen beschikbaar")
            st.write(f"- Gemiddeld {course_analysis['total_choices'] / course_analysis['unique_courses']:.1f} keuzes per cursus")
    
    # Recent course choices
    st.subheader("🕒 Recent Course Choices")
    
    recent_choices = course_analysis['course_details'][-10:]  # Laatste 10 keuzes
    if recent_choices:
        recent_df = pd.DataFrame(recent_choices)
        recent_df['chosen_at'] = pd.to_datetime(recent_df['chosen_at'])
        recent_df = recent_df.sort_values('chosen_at', ascending=False)
        
        # Toon recente keuzes
        for _, choice in recent_df.iterrows():
            st.write(f"📚 **{choice['course_name']}** - Transcript: {choice['transcript_id'][:8]}...")
    
    # Export functionaliteit
    st.subheader("📥 Export Course Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📊 Export Course Analysis"):
            # Maak export data
            export_data = {
                'analysis_date': datetime.now().isoformat(),
                'total_choices': course_analysis['total_choices'],
                'unique_courses': course_analysis['unique_courses'],
                'course_rankings': course_table_data,
                'detailed_choices': course_analysis['course_details']
            }
            
            # Export naar JSON
            import json
            with open('course_analysis_export.json', 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            st.success("✅ Course analysis geëxporteerd naar 'course_analysis_export.json'")
    
    with col2:
        if st.button("📈 Download Course CSV"):
            # Maak CSV van course rankings
            csv_data = df_courses.to_csv(index=False)
            st.download_button(
                label="Download Course Rankings CSV",
                data=csv_data,
                file_name=f"course_rankings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )

# ===== COMPREHENSIVE REPORT GENERATION =====
def generate_transcript_report(complete_data, df_evaluations):
    """Genereer een uitgebreide transcript rapportage"""
    if not complete_data:
        return None
    
    transcripts = complete_data.get('transcripts', [])
    evaluation_results = complete_data.get('evaluation_results', [])
    
    if not transcripts:
        return None
    
    # Samenvatting van alle transcripts
    report = {
        'generated_at': datetime.now().isoformat(),
        'total_transcripts': len(transcripts),
        'total_evaluations': len(evaluation_results),
        'summary': {},
        'ai_performance_analysis': {},
        'sample_conversations': [],
        'evaluation_results': {},
        'highlights': []
    }
    
    # AI Performance Analysis
    ai_errors = []
    ai_successes = []
    
    for transcript in transcripts:
        transcript_id = transcript.get('id', 'Unknown')
        evaluations = transcript.get('evaluations', [])
        
        # Check voor AI fouten (bijvoorbeeld lage scores of negatieve feedback)
        for eval_item in evaluations:
            eval_name = eval_item.get('name', '')
            eval_value = eval_item.get('value')
            
            # Identificeer mogelijke AI fouten
            if eval_name == 'Conversation quality' and isinstance(eval_value, (int, float)):
                if eval_value < 3:  # Laag score
                    ai_errors.append({
                        'transcript_id': transcript_id,
                        'issue': f'Lage conversatie kwaliteit: {eval_value}/5',
                        'evaluation': eval_name,
                        'value': eval_value
                    })
                elif eval_value >= 4:  # Hoog score
                    ai_successes.append({
                        'transcript_id': transcript_id,
                        'achievement': f'Hoge conversatie kwaliteit: {eval_value}/5',
                        'evaluation': eval_name,
                        'value': eval_value
                    })
            
            elif eval_name == 'User satisfaction' and isinstance(eval_value, (int, float)):
                if eval_value < 3:
                    ai_errors.append({
                        'transcript_id': transcript_id,
                        'issue': f'Lage gebruikersatisfactie: {eval_value}/5',
                        'evaluation': eval_name,
                        'value': eval_value
                    })
    
    report['ai_performance_analysis'] = {
        'total_errors': len(ai_errors),
        'total_successes': len(ai_successes),
        'error_rate': (len(ai_errors) / len(transcripts)) * 100 if transcripts else 0,
        'success_rate': (len(ai_successes) / len(transcripts)) * 100 if transcripts else 0,
        'errors': ai_errors,
        'successes': ai_successes
    }
    
    # Sample conversations (steekproef van 5 transcripts)
    import random
    sample_size = min(5, len(transcripts))
    sample_transcripts = random.sample(transcripts, sample_size) if transcripts else []
    
    for transcript in sample_transcripts:
        sample_convo = {
            'transcript_id': transcript.get('id', 'Unknown'),
            'session_id': transcript.get('sessionID', 'Unknown'),
            'created_at': transcript.get('createdAt', 'Unknown'),
            'evaluations': transcript.get('evaluations', []),
            'properties': transcript.get('properties', []),
            'summary': f"Transcript met {len(transcript.get('evaluations', []))} evaluaties"
        }
        report['sample_conversations'].append(sample_convo)
    
    # Evaluation results samenvatting
    eval_summary = {}
    for result in evaluation_results:
        eval_name = result['evaluation_name']
        eval_value = result['evaluation_value']
        
        if eval_name not in eval_summary:
            eval_summary[eval_name] = {
                'total_runs': 0,
                'values': [],
                'value_distribution': {}
            }
        
        eval_summary[eval_name]['total_runs'] += 1
        eval_summary[eval_name]['values'].append(eval_value)
        
        # Value distribution
        if eval_value in eval_summary[eval_name]['value_distribution']:
            eval_summary[eval_name]['value_distribution'][eval_value] += 1
        else:
            eval_summary[eval_name]['value_distribution'][eval_value] = 1
    
    report['evaluation_results'] = eval_summary
    
    # Highlights en insights
    highlights = []
    
    # AI Performance highlights
    if ai_errors:
        highlights.append(f"🚨 {len(ai_errors)} AI fouten gedetecteerd - aandacht vereist")
    
    if ai_successes:
        highlights.append(f"✅ {len(ai_successes)} succesvolle AI interacties")
    
    # Course choice highlights
    course_analysis = analyze_course_choices(evaluation_results)
    if course_analysis and course_analysis['sorted_courses']:
        top_course = course_analysis['sorted_courses'][0]
        highlights.append(f"🎯 Meest populaire cursus: {top_course[0]} ({top_course[1]} keuzes)")
    
    # Evaluation highlights
    for eval_name, data in eval_summary.items():
        if data['total_runs'] > 0:
            avg_value = sum(data['values']) / len(data['values']) if data['values'] else 0
            highlights.append(f"📊 {eval_name}: {data['total_runs']} runs, gemiddelde: {avg_value:.2f}")
    
    report['highlights'] = highlights
    
    return report

def show_report_generation(complete_data, df_evaluations):
    """Toon rapportage generatie en download opties"""
    st.header("📋 Comprehensive Transcript Report")
    st.markdown("Genereer een uitgebreide rapportage van alle transcripts met AI performance analyse en highlights.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔍 Generate Report", type="primary"):
            with st.spinner("Genereren van uitgebreide rapportage..."):
                report = generate_transcript_report(complete_data, df_evaluations)
                
                if report:
                    st.session_state['generated_report'] = report
                    st.success("✅ Rapportage succesvol gegenereerd!")
                else:
                    st.error("❌ Kon geen rapportage genereren")
    
    with col2:
        if st.button("📊 Download Report"):
            if 'generated_report' in st.session_state:
                report = st.session_state['generated_report']
                
                # Maak JSON download
                import json
                json_data = json.dumps(report, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download Full Report (JSON)",
                    data=json_data,
                    file_name=f"transcript_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                # Maak ook een samenvatting PDF (als CSV voor nu)
                summary_data = f"""
Transcript Report Samenvatting
Generated: {report['generated_at']}

OVERZICHT:
- Totaal Transcripts: {report['total_transcripts']}
- Totaal Evaluaties: {report['total_evaluation_results']}

AI PERFORMANCE:
- Fouten gedetecteerd: {report['ai_performance_analysis']['total_errors']}
- Succesvolle interacties: {report['ai_performance_analysis']['total_successes']}
- Fout percentage: {report['ai_performance_analysis']['error_rate']:.1f}%
- Succes percentage: {report['ai_performance_analysis']['success_rate']:.1f}%

HIGHLIGHTS:
{chr(10).join(report['highlights'])}

SAMPLE CONVERSATIONS:
{chr(10).join([f"- {conv['transcript_id']}: {conv['summary']}" for conv in report['sample_conversations']])}
"""
                
                st.download_button(
                    label="📄 Download Summary (TXT)",
                    data=summary_data,
                    file_name=f"transcript_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            else:
                st.warning("⚠️ Genereer eerst een rapportage")
    
    # Toon rapportage preview
    if 'generated_report' in st.session_state:
        report = st.session_state['generated_report']
        
        st.subheader("📊 Report Preview")
        
        # AI Performance Overview
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Transcripts", report['total_transcripts'])
        
        with col2:
            st.metric("AI Errors", report['ai_performance_analysis']['total_errors'])
        
        with col3:
            st.metric("AI Successes", report['ai_performance_analysis']['total_successes'])
        
        with col4:
            error_rate = report['ai_performance_analysis']['error_rate']
            st.metric("Error Rate", f"{error_rate:.1f}%")
        
        # Highlights
        st.subheader("💡 Key Highlights")
        for highlight in report['highlights']:
            st.write(f"• {highlight}")
        
        # Sample conversations
        st.subheader("🔍 Sample Conversations")
        for conv in report['sample_conversations']:
            with st.expander(f"Transcript {conv['transcript_id']}"):
                st.write(f"**Session ID:** {conv['session_id']}")
                st.write(f"**Created:** {conv['created_at']}")
                st.write(f"**Evaluations:** {len(conv['evaluations'])}")
                st.write(f"**Properties:** {len(conv['properties'])}")
                st.write(f"**Summary:** {conv['summary']}")
        
        # AI Errors details
        if report['ai_performance_analysis']['errors']:
            st.subheader("🚨 AI Errors Details")
            for error in report['ai_performance_analysis']['errors']:
                st.write(f"• **{error['transcript_id']}**: {error['issue']}")

# ===== TRANSCRIPTS PAGE =====
def get_transcripts_page_data(analytics, page_size=30, current_page=0):
    """Haal transcripts op voor de transcripts pagina met paginering"""
    try:
        # Bereken skip voor paginering
        skip = current_page * page_size
        
        # Haal transcripts op met paginering
        response = analytics.get_all_project_transcripts(
            take=page_size,
            skip=skip,
            order="DESC"
        )
        
        transcripts = response.get('transcripts', [])
        total_count = response.get('total', 0)
        
        return {
            'transcripts': transcripts,
            'total_count': total_count,
            'current_page': current_page,
            'has_more': len(transcripts) == page_size and (skip + page_size) < total_count
        }
        
    except Exception as e:
        st.error(f"Fout bij ophalen transcripts: {e}")
        return None

def format_transcript_for_display(transcript):
    """Format transcript data voor weergave"""
    # Haal chat berichten op voor message count
    message_count = 0
    try:
        analytics = AIBotAnalytics()
        messages = analytics.get_transcript_messages(transcript.get('id', ''))
        message_count = len(messages) if messages else 0
    except:
        message_count = 0
    
    return {
        'id': transcript.get('id', 'Unknown'),
        'session_id': transcript.get('sessionID', 'Unknown'),
        'created_at': transcript.get('createdAt', 'Unknown'),
        'ended_at': transcript.get('endedAt', 'Unknown'),
        'evaluations_count': len(transcript.get('evaluations', [])),
        'properties_count': len(transcript.get('properties', [])),
        'messages_count': message_count,
        'has_recording': bool(transcript.get('recordingURL')),
        'recording_url': transcript.get('recordingURL', ''),
        'evaluations': transcript.get('evaluations', []),
        'properties': transcript.get('properties', [])
    }

def show_transcript_details(transcript_data):
    """Toon gedetailleerde transcript informatie inclusief chat berichten"""
    with st.expander(f"📋 Transcript Details - {transcript_data['id'][:8]}...", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**📅 Basic Info:**")
            st.write(f"• **ID:** {transcript_data['id']}")
            st.write(f"• **Session:** {transcript_data['session_id']}")
            st.write(f"• **Created:** {transcript_data['created_at']}")
            st.write(f"• **Ended:** {transcript_data['ended_at']}")
        
        with col2:
            st.write("**📊 Statistics:**")
            st.write(f"• **Evaluations:** {transcript_data['evaluations_count']}")
            st.write(f"• **Properties:** {transcript_data['properties_count']}")
            st.write(f"• **Recording:** {'✅ Yes' if transcript_data['has_recording'] else '❌ No'}")
        
        # Chat Messages Section
        st.write("**💬 Chat Messages:**")
        
        # Haal chat berichten op
        try:
            analytics = AIBotAnalytics()
            messages = analytics.get_transcript_messages(transcript_data['id'])
            
            if messages:
                # Filter alleen berichten met betekenisvolle content
                meaningful_messages = []
                
                for message in messages:
                    message_type = message.get('type', '').lower()
                    payload = message.get('payload', {})
                    
                    # Skip lege berichten
                    if not payload or payload == {}:
                        continue
                    
                    # Check voor betekenisvolle content
                    has_content = False
                    
                    if message_type == 'trace':
                        content = payload.get('text', payload.get('message', payload.get('content', '')))
                        if content and content.strip():
                            has_content = True
                    elif message_type == 'action':
                        action_name = payload.get('name', payload.get('type', ''))
                        if action_name and action_name.strip():
                            has_content = True
                    elif message_type in ['text', 'message', 'user_input', 'user', 'speak', 'bot_response', 'ai_response', 'assistant', 'bot']:
                        content = payload.get('text', payload.get('message', payload.get('content', '')))
                        if content and content.strip():
                            has_content = True
                    elif message_type in ['intent', 'intent_request']:
                        intent = payload.get('intent', payload.get('name', ''))
                        if intent and intent.strip():
                            has_content = True
                    elif message_type in ['set', 'variable_set']:
                        var_name = payload.get('name', '')
                        var_value = payload.get('value', '')
                        if var_name and var_name.strip():
                            has_content = True
                    elif message_type == 'end':
                        has_content = True  # End messages zijn altijd betekenisvol
                    
                    if has_content:
                        meaningful_messages.append(message)
                
                # Toon alleen betekenisvolle berichten
                if meaningful_messages:
                    for i, message in enumerate(meaningful_messages):
                        message_type = message.get('type', '').lower()
                        payload = message.get('payload', {})
                        
                        if message_type == 'trace':
                            content = payload.get('text', payload.get('message', payload.get('content', str(payload))))
                            st.markdown(f"""
                            <div style="background-color: #e8f5e8; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                <strong>📊 Trace:</strong> {content}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        elif message_type == 'action':
                            action_name = payload.get('name', payload.get('type', 'Unknown action'))
                            st.markdown(f"""
                            <div style="background-color: #fff3e0; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                <strong>⚡ Action:</strong> {action_name}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        elif message_type == 'end':
                            st.markdown(f"""
                            <div style="background-color: #ffebee; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                <strong>🏁 End:</strong> Conversation ended
                            </div>
                            """, unsafe_allow_html=True)
                            
                        elif message_type in ['text', 'message', 'user_input', 'user']:
                            content = payload.get('text', payload.get('message', payload.get('content', 'No content')))
                            st.markdown(f"""
                            <div style="background-color: #e3f2fd; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                <strong>👤 User:</strong> {content}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        elif message_type in ['speak', 'bot_response', 'ai_response', 'assistant', 'bot']:
                            content = payload.get('text', payload.get('message', payload.get('content', 'No content')))
                            st.markdown(f"""
                            <div style="background-color: #f3e5f5; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                <strong>🤖 Bot:</strong> {content}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        elif message_type in ['intent', 'intent_request']:
                            intent = payload.get('intent', payload.get('name', 'Unknown intent'))
                            st.markdown(f"""
                            <div style="background-color: #fff3e0; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                <strong>🎯 Intent:</strong> {intent}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        elif message_type in ['set', 'variable_set']:
                            var_name = payload.get('name', 'Unknown variable')
                            var_value = payload.get('value', 'No value')
                            st.markdown(f"""
                            <div style="background-color: #e8f5e8; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                <strong>📝 Variable:</strong> {var_name} = {var_value}
                            </div>
                            """, unsafe_allow_html=True)
                            
                        else:
                            st.markdown(f"""
                            <div style="background-color: #f5f5f5; padding: 10px; border-radius: 10px; margin: 5px 0;">
                                <strong>❓ {message_type.title()}:</strong> {str(payload)[:200]}...
                            </div>
                            """, unsafe_allow_html=True)
                    
                    st.write(f"**📊 Meaningful Messages:** {len(meaningful_messages)} of {len(messages)} total logs")
                else:
                    st.info("Geen betekenisvolle chat berichten gevonden in dit transcript.")
                
            else:
                st.info("Geen chat logs gevonden voor dit transcript.")
                # Debug informatie toevoegen
                st.write("**🔍 Debug Info:**")
                try:
                    analytics = AIBotAnalytics()
                    # Probeer de reguliere transcript data op te halen
                    url = f"{analytics.base_url}/transcript/{transcript_data['id']}"
                    response = requests.get(url, headers=analytics._get_headers())
                    if response.status_code == 200:
                        data = response.json()
                        st.write("**Available keys in response:**")
                        st.write(list(data.keys()) if isinstance(data, dict) else "Not a dict")
                        
                        # Toon transcript data als die er is
                        if 'transcript' in data:
                            transcript_info = data['transcript']
                            st.write("**Available keys in transcript data:**")
                            st.write(list(transcript_info.keys()) if isinstance(transcript_info, dict) else "Not a dict")
                            
                            # Toon een voorbeeld van de logs data
                            if 'logs' in transcript_info:
                                logs_sample = transcript_info['logs'][:3] if len(transcript_info['logs']) > 3 else transcript_info['logs']
                                st.write("**Sample logs data:**")
                                st.write(logs_sample)
                            
                            st.write("**Transcript data preview:**")
                            st.write(str(transcript_info)[:1000] + "..." if len(str(transcript_info)) > 1000 else str(transcript_info))
                        else:
                            st.write("**Data preview:**")
                            st.write(str(data)[:1000] + "..." if len(str(data)) > 1000 else str(data))
                    else:
                        st.write(f"**API Error:** Status {response.status_code}")
                        st.write(f"**Response:** {response.text}")
                except Exception as e:
                    st.write(f"**Error:** {e}")
                
        except Exception as e:
            st.error(f"Fout bij ophalen chat logs: {e}")
            st.info("Toon alleen transcript metadata.")
        
        # Evaluations details (als backup)
        if transcript_data['evaluations']:
            st.write("**🔍 Evaluations:**")
            eval_df = pd.DataFrame(transcript_data['evaluations'])
            st.dataframe(eval_df, use_container_width=True)
        
        # Properties details
        if transcript_data['properties']:
            st.write("**🏷️ Properties:**")
            prop_df = pd.DataFrame(transcript_data['properties'])
            st.dataframe(prop_df, use_container_width=True)
        
        # Recording link
        if transcript_data['has_recording'] and transcript_data['recording_url']:
            st.write("**🎵 Recording:**")
            st.link_button("🔗 Listen to Recording", transcript_data['recording_url'])

def show_transcripts_page():
    """Toon de transcripts pagina met lazy loading"""
    st.header("📝 Transcripts Archive")
    st.markdown("Bekijk alle transcripts uit de AI Bot API met gedetailleerde informatie.")
    
    # Initialize session state voor paginering
    if 'transcripts_page' not in st.session_state:
        st.session_state.transcripts_page = 0
    if 'transcripts_data' not in st.session_state:
        st.session_state.transcripts_data = []
    if 'total_transcripts' not in st.session_state:
        st.session_state.total_transcripts = 0
    
    # API check
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = os.getenv('VOICEFLOW_PROJECT_ID')
    
    if not api_key or not project_id:
        st.error("❌ VOICEFLOW_API_KEY of VOICEFLOW_PROJECT_ID niet geconfigureerd")
        return
    
    # Initialize analytics
    try:
        analytics = AIBotAnalytics()
    except Exception as e:
        st.error(f"❌ Fout bij initialiseren analytics: {e}")
        return
    
    # Load more button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔄 Load More Transcripts", type="primary"):
            with st.spinner("Laden van meer transcripts..."):
                page_data = get_transcripts_page_data(
                    analytics, 
                    page_size=30, 
                    current_page=st.session_state.transcripts_page
                )
                
                if page_data and page_data['transcripts']:
                    st.session_state.transcripts_data.extend(page_data['transcripts'])
                    st.session_state.transcripts_page += 1
                    st.session_state.total_transcripts = page_data['total_count']
                    st.success(f"✅ {len(page_data['transcripts'])} transcripts geladen!")
                else:
                    st.warning("⚠️ Geen meer transcripts beschikbaar")
    
    # Reset button
    with col3:
        if st.button("🔄 Reset"):
            st.session_state.transcripts_page = 0
            st.session_state.transcripts_data = []
            st.session_state.total_transcripts = 0
            st.rerun()
    
    # Load initial data if empty
    if not st.session_state.transcripts_data:
        with st.spinner("Laden van eerste 30 transcripts..."):
            page_data = get_transcripts_page_data(analytics, page_size=30, current_page=0)
            
            if page_data and page_data['transcripts']:
                st.session_state.transcripts_data = page_data['transcripts']
                st.session_state.transcripts_page = 1
                st.session_state.total_transcripts = page_data['total_count']
            else:
                st.error("❌ Kon geen transcripts ophalen")
                return
    
    # Overview metrics
    st.subheader("📊 Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Loaded Transcripts", len(st.session_state.transcripts_data))
    
    with col2:
        st.metric("Total Available", st.session_state.total_transcripts)
    
    with col3:
        st.metric("Current Page", st.session_state.transcripts_page)
    
    with col4:
        remaining = st.session_state.total_transcripts - len(st.session_state.transcripts_data)
        st.metric("Remaining", max(0, remaining))
    
    with col5:
        # Bereken totaal aantal berichten
        total_messages = sum(t.get('messages_count', 0) for t in st.session_state.transcripts_data)
        st.metric("Total Messages", total_messages)
    
    # Search and filter
    st.subheader("🔍 Search & Filter")
    col1, col2 = st.columns(2)
    
    with col1:
        search_term = st.text_input("🔍 Search by Session ID or Transcript ID", placeholder="Enter ID...")
    
    with col2:
        filter_evaluations = st.multiselect(
            "📊 Filter by Evaluation Type",
            options=["All", "AI course chosen", "Conversation quality", "User satisfaction"],
            default=["All"]
        )
    
    # Filter transcripts
    filtered_transcripts = st.session_state.transcripts_data
    
    # Apply search filter
    if search_term:
        filtered_transcripts = [
            t for t in filtered_transcripts 
            if search_term.lower() in t.get('sessionID', '').lower() 
            or search_term.lower() in t.get('id', '').lower()
        ]
    
    # Apply evaluation filter
    if "All" not in filter_evaluations:
        filtered_transcripts = [
            t for t in filtered_transcripts
            if any(eval_item.get('name') in filter_evaluations 
                   for eval_item in t.get('evaluations', []))
        ]
    
    # Display transcripts
    st.subheader(f"📝 Transcripts ({len(filtered_transcripts)} shown)")
    
    if not filtered_transcripts:
        st.info("Geen transcripts gevonden met de huidige filters.")
        return
    
    # Sort by creation date (newest first)
    filtered_transcripts.sort(key=lambda x: x.get('createdAt', ''), reverse=True)
    
    # Display each transcript
    for i, transcript in enumerate(filtered_transcripts):
        formatted_transcript = format_transcript_for_display(transcript)
        
        # Create a card-like display
        with st.container():
            st.markdown("---")
            
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.write(f"**📝 Transcript {i+1}**")
                st.write(f"**ID:** {formatted_transcript['id'][:12]}...")
                st.write(f"**Session:** {formatted_transcript['session_id'][:12]}...")
            
            with col2:
                st.write("**📅 Created:**")
                created_date = formatted_transcript['created_at']
                if created_date != 'Unknown':
                    try:
                        date_obj = datetime.fromisoformat(created_date.replace('Z', '+00:00'))
                        st.write(date_obj.strftime("%Y-%m-%d %H:%M"))
                    except:
                        st.write(created_date)
                else:
                    st.write("Unknown")
            
            with col3:
                st.write("**📊 Stats:**")
                st.write(f"Evals: {formatted_transcript['evaluations_count']}")
                st.write(f"Props: {formatted_transcript['properties_count']}")
                st.write(f"Messages: {formatted_transcript['messages_count']}")
            
            with col4:
                st.write("**🎵 Recording:**")
                if formatted_transcript['has_recording']:
                    st.success("✅ Available")
                else:
                    st.info("❌ None")
            
            # Show details button
            show_transcript_details(formatted_transcript)
    
    # Load more indicator
    if st.session_state.total_transcripts > len(st.session_state.transcripts_data):
        st.info(f"📄 {st.session_state.total_transcripts - len(st.session_state.transcripts_data)} meer transcripts beschikbaar. Klik 'Load More' om meer te laden.")

# ===== MAIN DASHBOARD =====
def main():
    st.set_page_config(
        page_title="AI Bot Analytics Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Environment check
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = os.getenv('VOICEFLOW_PROJECT_ID')
    
    if not api_key or not project_id:
        st.error("❌ VOICEFLOW_API_KEY of VOICEFLOW_PROJECT_ID niet geconfigureerd in .env")
        st.stop()
    
    # Main title
    st.title("📊 AI Bot Analytics Dashboard")
    st.markdown("**Alleen echte data uit de AI Bot API**")
    
    # Navbar met tabs
    tab1, tab2 = st.tabs(["📈 Main Dashboard", "📝 Transcripts Archive"])
    
    with tab1:
        show_main_dashboard()
    
    with tab2:
        show_transcripts_page()

def show_main_dashboard():
    """Toon het hoofd dashboard"""
    # Data ophalen
    with st.spinner("🔄 Echte AI Bot data ophalen..."):
        complete_data = get_real_voiceflow_data()
        evaluations = get_evaluations_data()
        transcripts = get_transcripts_data()
    
    if not complete_data:
        st.error("❌ Kon geen data ophalen van AI Bot API")
        st.stop()
    
    # Data verwerken
    df_transcripts = process_transcript_data(transcripts)
    df_evaluations = process_evaluation_data(evaluations)
    
    # ===== METRICS SECTIE =====
    st.header("📊 Overzicht Metrics")
    
    summary = complete_data.get('summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_transcripts = summary.get('total_transcripts', 0)
        st.metric("Totaal Transcripts", total_transcripts)
    
    with col2:
        total_evaluations = summary.get('total_evaluations', 0)
        st.metric("Totaal Evaluaties", total_evaluations)
    
    with col3:
        total_eval_results = summary.get('total_evaluation_results', 0)
        st.metric("Evaluatie Resultaten", total_eval_results)
    
    with col4:
        if df_transcripts is not None and not df_transcripts.empty:
            unique_sessions = df_transcripts['session_id'].nunique()
            st.metric("Unieke Sessions", unique_sessions)
        else:
            st.metric("Unieke Sessions", 0)
    
    # ===== TRANSCRIPT ANALYTICS =====
    st.header("📝 Transcript Analytics")
    
    if df_transcripts is not None and not df_transcripts.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Transcripts per dag
            daily_counts = df_transcripts.groupby('date').size().reset_index(name='count')
            fig_daily = px.line(
                daily_counts, 
                x='date', 
                y='count',
                title="Transcripts per Dag",
                labels={'date': 'Datum', 'count': 'Aantal Transcripts'}
            )
            st.plotly_chart(fig_daily, use_container_width=True)
        
        with col2:
            # Evaluations per transcript
            eval_counts = df_transcripts['evaluations_count'].value_counts()
            fig_eval = px.bar(
                x=eval_counts.index,
                y=eval_counts.values,
                title="Evaluations per Transcript",
                labels={'x': 'Aantal Evaluations', 'y': 'Aantal Transcripts'}
            )
            st.plotly_chart(fig_eval, use_container_width=True)
    
    # ===== EVALUATION ANALYTICS =====
    st.header("📋 Evaluation Analytics")
    
    if df_evaluations is not None and not df_evaluations.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            # Evaluation types
            type_counts = df_evaluations['type'].value_counts()
            fig_types = px.pie(
                values=type_counts.values,
                names=type_counts.index,
                title="Evaluation Types"
            )
            st.plotly_chart(fig_types, use_container_width=True)
        
        with col2:
            # Enabled vs disabled evaluations
            enabled_counts = df_evaluations['enabled'].value_counts()
            fig_enabled = px.bar(
                x=['Enabled', 'Disabled'],
                y=[enabled_counts.get(True, 0), enabled_counts.get(False, 0)],
                title="Enabled vs Disabled Evaluations",
                labels={'x': 'Status', 'y': 'Aantal'}
            )
            st.plotly_chart(fig_enabled, use_container_width=True)
    
    # ===== EVALUATION RESULTS =====
    show_enhanced_evaluation_results(complete_data, df_evaluations)

    # ===== COURSE ANALYTICS =====
    show_course_analytics(complete_data)
    
    # ===== COMPREHENSIVE REPORT GENERATION =====
    show_report_generation(complete_data, df_evaluations)
    
    # ===== TRANSCRIPTS PAGE =====
    # show_transcripts_page() # This is now handled by the main function's page routing
    
    # ===== RAW DATA SECTIE =====
    st.header("📋 Raw Data")
    
    tab1, tab2, tab3 = st.columns(3)
    
    with tab1:
        st.subheader("Transcripts")
        if df_transcripts is not None and not df_transcripts.empty:
            st.dataframe(df_transcripts.head(10))
        else:
            st.info("Geen transcript data beschikbaar")
    
    with tab2:
        st.subheader("Evaluations")
        if df_evaluations is not None and not df_evaluations.empty:
            st.dataframe(df_evaluations)
        else:
            st.info("Geen evaluation data beschikbaar")
    
    with tab3:
        st.subheader("Evaluation Results")
        evaluation_results = complete_data.get('evaluation_results', [])
        if evaluation_results:
            df_results = pd.DataFrame(evaluation_results)
            st.dataframe(df_results.head(10))
        else:
            st.info("Geen evaluation resultaten beschikbaar")

if __name__ == "__main__":
    main() 