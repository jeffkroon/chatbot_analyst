#!/usr/bin/env python3
"""
Voiceflow Analytics Dashboard - Alleen echte data uit de API
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from voiceflow_analytics import VoiceflowAnalytics

# Load environment variables
load_dotenv()

# ===== API FUNCTIES =====
def get_real_voiceflow_data():
    """Haal echte data op van Voiceflow API"""
    try:
        analytics = VoiceflowAnalytics()
        
        # Haal complete project data op
        complete_data = analytics.get_complete_project_data(
            batch_size=100,
            export_filename="dashboard_data.json"
        )
        
        return complete_data
        
    except Exception as e:
        st.error(f"Fout bij ophalen Voiceflow data: {e}")
        return None

def get_evaluations_data():
    """Haal evaluaties op van Voiceflow API"""
    try:
        analytics = VoiceflowAnalytics()
        evaluations = analytics.get_all_evaluations()
        return evaluations.get('evaluations', [])
        
    except Exception as e:
        st.error(f"Fout bij ophalen evaluaties: {e}")
        return []

def get_transcripts_data():
    """Haal transcripts op van Voiceflow API"""
    try:
        analytics = VoiceflowAnalytics()
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
    
    # Summary table
    st.subheader("📋 Summary Table")
    summary_data = []
    for eval_name, data in eval_analysis.items():
        summary_row = {
            'Evaluation': eval_name,
            'Type': data['type'],
            'Total Runs': data['total_runs'],
        }
        
        if data['success_rate'] is not None:
            summary_row['Success Rate'] = f"{data['success_rate']:.1f}%"
        
        if data['avg_rating'] is not None:
            summary_row['Avg Rating'] = f"{data['avg_rating']:.2f}"
        
        summary_data.append(summary_row)
    
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True)

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
        
        if course_name in course_counts:
            course_counts[course_name] += 1
        else:
            course_counts[course_name] = 1
        
        course_details.append({
            'course_name': course_name,
            'transcript_id': transcript_id,
            'chosen_at': datetime.now().isoformat()  # We hebben geen timestamp, dus gebruiken we nu
        })
    
    # Sorteer op populariteit
    sorted_courses = sorted(course_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'total_choices': len(course_results),
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
    
    if not course_analysis:
        st.info("Geen course keuze data beschikbaar")
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
        # Top 10 cursussen
        top_courses = course_analysis['sorted_courses'][:10]
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
    
    # Maak een mooie tabel met alle cursussen
    course_table_data = []
    for i, (course_name, count) in enumerate(course_analysis['sorted_courses']):
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
    
    if course_analysis['sorted_courses']:
        top_course = course_analysis['sorted_courses'][0]
        top_percentage = (top_course[1] / course_analysis['total_choices']) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🏆 Most Popular Course:**")
            st.write(f"**{top_course[0]}** wordt het meest gekozen")
            st.write(f"- {top_course[1]} keer gekozen ({top_percentage:.1f}%)")
            st.write(f"- Dit is de favoriete cursus van de AI")
        
        with col2:
            st.write("**📊 Distribution Insights:**")
            if len(course_analysis['sorted_courses']) >= 3:
                top_3_total = sum(course[1] for course in course_analysis['sorted_courses'][:3])
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

# ===== MAIN DASHBOARD =====
def main():
    st.set_page_config(
        page_title="Voiceflow Analytics Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Voiceflow Analytics Dashboard")
    st.markdown("**Alleen echte data uit de Voiceflow API**")
    
    # Environment check
    api_key = os.getenv('VOICEFLOW_API_KEY')
    project_id = os.getenv('VOICEFLOW_PROJECT_ID')
    
    if not api_key or not project_id:
        st.error("❌ VOICEFLOW_API_KEY of VOICEFLOW_PROJECT_ID niet geconfigureerd in .env")
        st.stop()
    
    # Data ophalen
    with st.spinner("🔄 Echte Voiceflow data ophalen..."):
        complete_data = get_real_voiceflow_data()
        evaluations = get_evaluations_data()
        transcripts = get_transcripts_data()
    
    if not complete_data:
        st.error("❌ Kon geen data ophalen van Voiceflow API")
        st.stop()
    
    # Data verwerken
    df_transcripts = process_transcript_data(transcripts)
    df_evaluations = process_evaluation_data(evaluations)
    
    # ===== API STATUS SECTIE =====
    st.header("🔌 API Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if complete_data:
            st.success("✅ Voiceflow Analytics API")
            st.metric("Status", "Actief")
            st.metric("Transcripts", complete_data.get('summary', {}).get('total_transcripts', 0))
        else:
            st.error("❌ Voiceflow Analytics API")
            st.metric("Status", "Error")
    
    with col2:
        if evaluations:
            st.success("✅ Evaluations API")
            st.metric("Evaluations", len(evaluations))
        else:
            st.warning("⚠️ Evaluations API")
            st.metric("Status", "Niet beschikbaar")
    
    with col3:
        if transcripts:
            st.success("✅ Transcripts API")
            st.metric("Transcripts", len(transcripts))
        else:
            st.warning("⚠️ Transcripts API")
            st.metric("Status", "Niet beschikbaar")
    
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