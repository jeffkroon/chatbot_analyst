import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from voiceflow_analytics import VoiceflowAnalytics
from database import AnalyticsDatabase

# Page config
st.set_page_config(
    page_title="Voiceflow Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize components
@st.cache_resource
def init_components():
    """Initialize analytics components"""
    try:
        analytics = VoiceflowAnalytics()
        database = AnalyticsDatabase()
        return analytics, database
    except Exception as e:
        st.error(f"Fout bij initialiseren: {e}")
        return None, None

# Main dashboard
def main():
    st.title("📊 Voiceflow Analytics Dashboard")
    st.markdown("---")
    
    # Initialize components
    analytics, database = init_components()
    
    if not analytics or not database:
        st.error("Kan analytics componenten niet initialiseren. Controleer je .env configuratie.")
        return
    
    # Sidebar controls
    st.sidebar.header("⚙️ Instellingen")
    
    # Time period selector
    days_back = st.sidebar.selectbox(
        "Analyse periode",
        [7, 14, 30, 60, 90],
        index=2,
        help="Selecteer hoeveel dagen terug je wilt analyseren"
    )
    
    # Refresh button
    if st.sidebar.button("🔄 Vernieuw Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📈 Analytics Overzicht")
        
        # Get analytics summary
        try:
            summary = database.get_analytics_summary(days_back)
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Totaal Transcripts",
                    summary['conversion_rates']['total_conversations']
                )
            
            with col2:
                st.metric(
                    "Succesvolle Conversies",
                    summary['conversion_rates']['successful_conversions']
                )
            
            with col3:
                st.metric(
                    "Conversie Rate",
                    f"{summary['conversion_rates']['conversion_rate']:.1f}%"
                )
            
            with col4:
                st.metric(
                    "Populaire Cursussen",
                    len(summary['popular_courses'])
                )
            
            # Popular courses chart
            st.subheader("🏆 Populairste Cursussen")
            if summary['popular_courses']:
                courses_df = pd.DataFrame(summary['popular_courses'])
                
                fig = px.bar(
                    courses_df,
                    x='course_name',
                    y='mentions',
                    title="Cursussen per aantal mentions",
                    color='mentions',
                    color_continuous_scale='viridis'
                )
                fig.update_layout(
                    xaxis_title="Cursus",
                    yaxis_title="Aantal Mentions",
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nog geen cursus data beschikbaar")
            
            # Common questions
            st.subheader("❓ Meest Gestelde Vragen")
            if summary['common_questions']:
                questions_df = pd.DataFrame(summary['common_questions'])
                
                fig = px.pie(
                    questions_df,
                    values='count',
                    names='question_type',
                    title="Verdeling van vraagtypes"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Nog geen vraag analyse beschikbaar")
            
        except Exception as e:
            st.error(f"Fout bij ophalen analytics: {e}")
    
    with col2:
        st.header("📋 Snelle Acties")
        
        # Manual analysis trigger
        if st.button("🔍 Start Nieuwe Analyse"):
            with st.spinner("Analyseren van conversaties..."):
                try:
                    results = analytics.analyze_conversations(days_back)
                    st.success(f"✅ Analyse voltooid! {results['total_transcripts']} transcripts geanalyseerd")
                    
                    # Store results in database
                    for eval_result in results.get('evaluation_results', []):
                        database.store_evaluation_result(eval_result)
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Fout bij analyseren: {e}")
        
        # Setup evaluations
        if st.button("⚙️ Setup Evaluaties"):
            with st.spinner("Instellen van evaluaties..."):
                try:
                    evaluations = analytics.setup_course_analysis_evaluations()
                    st.success(f"✅ Evaluaties ingesteld: {len(evaluations)} evaluaties aangemaakt")
                except Exception as e:
                    st.error(f"Fout bij instellen evaluaties: {e}")
        
        # Export data
        if st.button("📥 Export Data"):
            try:
                summary = database.get_analytics_summary(days_back)
                json_str = json.dumps(summary, indent=2, default=str)
                
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"voiceflow_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            except Exception as e:
                st.error(f"Fout bij exporteren: {e}")
    
    # Detailed analysis section
    st.markdown("---")
    st.header("🔍 Gedetailleerde Analyse")
    
    tab1, tab2, tab3 = st.tabs(["📊 Conversie Funnel", "📈 Trends", "📋 Raw Data"])
    
    with tab1:
        st.subheader("Conversie Funnel Analyse")
        
        try:
            conversion_data = summary['conversion_rates']
            
            # Create funnel chart
            fig = go.Figure(go.Funnel(
                y = ["Totaal Gesprekken", "Succesvolle Conversies"],
                x = [conversion_data['total_conversations'], conversion_data['successful_conversions']],
                textinfo = "value+percent initial"
            ))
            
            fig.update_layout(
                title="Conversie Funnel",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Conversion insights
            if conversion_data['total_conversations'] > 0:
                st.info(f"""
                **Insights:**
                - Van de {conversion_data['total_conversations']} gesprekken zijn er {conversion_data['successful_conversions']} succesvol
                - Conversie rate: {conversion_data['conversion_rate']:.1f}%
                """)
            
        except Exception as e:
            st.error(f"Fout bij conversie analyse: {e}")
    
    with tab2:
        st.subheader("Trend Analyse")
        
        # Placeholder for trend analysis
        st.info("Trend analyse functionaliteit komt binnenkort beschikbaar")
        
        # You could add time-series analysis here
        # For example, comparing data over different time periods
    
    with tab3:
        st.subheader("Raw Data Overzicht")
        
        try:
            # Show raw data in expandable sections
            with st.expander("📊 Populaire Cursussen Data"):
                if summary['popular_courses']:
                    st.dataframe(pd.DataFrame(summary['popular_courses']))
                else:
                    st.info("Geen cursus data beschikbaar")
            
            with st.expander("❓ Vraag Analyse Data"):
                if summary['common_questions']:
                    st.dataframe(pd.DataFrame(summary['common_questions']))
                else:
                    st.info("Geen vraag analyse data beschikbaar")
            
            with st.expander("📈 Conversie Data"):
                st.json(summary['conversion_rates'])
                
        except Exception as e:
            st.error(f"Fout bij tonen raw data: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
        <p>📊 Voiceflow Analytics Dashboard | Laatste update: {}</p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main() 