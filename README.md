# 🚀 Voiceflow Analytics Dashboard

Een krachtige Streamlit dashboard voor het analyseren van Voiceflow chatbot data, inclusief transcripts, evaluaties en course analytics.

## ✨ Features

- **📊 Real-time Analytics** - Echte data uit Voiceflow API
- **📈 Enhanced Evaluation Results** - Gedetailleerde evaluatie analyses
- **🎯 Course Analytics** - Visualisaties van course keuzes
- **📝 Transcript Analytics** - Dagelijkse distributie en patterns
- **🔌 API Status Monitoring** - Status van alle Voiceflow APIs
- **📥 Export Functionaliteit** - JSON en CSV exports

## 🛠️ Setup

### Lokale Development

1. **Clone de repository:**
```bash
git clone git@github.com:jeffkroon/chatbot_analyst.git
cd chatbot_analyst
```

2. **Installeer dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configureer environment variables:**
```bash
cp env_example.txt .env
# Vul je VOICEFLOW_API_KEY en VOICEFLOW_PROJECT_ID in
```

4. **Start de dashboard:**
```bash
streamlit run voiceflow_dashboard.py
```

### 🚀 Render Deployment

1. **Fork deze repository naar je GitHub account**

2. **Ga naar [Render.com](https://render.com) en maak een account**

3. **Maak een nieuwe Web Service:**
   - Connect je GitHub repository
   - Kies "Python" als environment
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run voiceflow_dashboard.py --server.port $PORT --server.address 0.0.0.0`

4. **Configureer Environment Variables in Render:**
   - `VOICEFLOW_API_KEY` - Je Voiceflow API key
   - `VOICEFLOW_PROJECT_ID` - Je Voiceflow project ID

5. **Deploy!** 🎉

## 📁 Project Structuur

```
chatbot_analyst/
├── voiceflow_dashboard.py      # Main Streamlit dashboard
├── voiceflow_analytics.py      # Voiceflow API client
├── get_transcripts.py          # Transcript processing
├── requirements.txt            # Python dependencies
├── render.yaml                # Render deployment config
├── Procfile                   # Alternative deployment config
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🔌 API Endpoints

### Transcript API
- **POST** `/v1/transcript/project/{projectID}` - Get all project transcripts
- **GET** `/v1/transcript-evaluation/project/{projectID}` - Get all evaluations

### Features
- **Pagination** - Automatische paginering voor grote datasets
- **Date Filtering** - Filter op start/end dates
- **Advanced Filtering** - Complexe filter opties
- **Real-time Data** - Geen mock data, alleen echte API data

## 📊 Dashboard Sections

### 🔌 API Status
- Status van alle Voiceflow APIs
- Connection monitoring
- Error handling

### 📊 Overview Metrics
- Totaal transcripts
- Totaal evaluaties
- Evaluatie resultaten
- Unieke sessions

### 📝 Transcript Analytics
- Dagelijkse transcript distributie
- Evaluations per transcript
- Session patterns

### 📋 Evaluation Analytics
- Evaluation types (boolean, number, string)
- Enabled vs disabled evaluations
- Performance metrics

### 📈 Enhanced Evaluation Results
- Gedetailleerde per-evaluatie analyses
- Success rates voor boolean evaluaties
- Average ratings voor number evaluaties
- Value distributions
- Recent results tracking

### 🎯 Course Analytics
- Course popularity charts
- Top course rankings
- Course choice insights
- Export functionaliteit

### 📋 Raw Data
- Transcript data
- Evaluation definitions
- Evaluation results

## 🧪 Testing

```bash
# Test de Voiceflow API
python test_transcript_api.py

# Test complete data fetching
python test_complete_data.py

# Test enhanced evaluations
python test_enhanced_evaluations.py
```

## 📈 Export Features

- **Course Analysis JSON** - Complete course analytics data
- **Course Rankings CSV** - Downloadbare course rankings
- **Dashboard Data JSON** - Complete project data export

## 🔧 Environment Variables

```bash
VOICEFLOW_API_KEY=your_api_key_here
VOICEFLOW_PROJECT_ID=your_project_id_here
```

## 🤝 Contributing

1. Fork de repository
2. Maak een feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit je changes (`git commit -m 'Add some AmazingFeature'`)
4. Push naar de branch (`git push origin feature/AmazingFeature`)
5. Open een Pull Request

## 📝 License

Dit project is open source en beschikbaar onder de MIT License.

## 🆘 Support

Voor vragen of problemen:
- Open een GitHub issue
- Check de Voiceflow API documentatie
- Controleer de environment variables

---

**Made with ❤️ voor Voiceflow Analytics** 