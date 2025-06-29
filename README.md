# Symphony AI Sleep Music Recommendation System

A comprehensive AI-powered sleep music recommendation system featuring LangGraph multi-agent workflows, personalized music generation, and A/B testing capabilities.

## 🎵 Overview

Symphony AI combines advanced AI technologies to provide personalized sleep music recommendations based on users' physiological and psychological states. The system uses a multi-agent architecture powered by LangGraph to analyze user inputs and generate tailored music recommendations.

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Models     │
│   (React)       │◄──►│   (Flask)       │◄──►│   (LangGraph)   │
│                 │    │                 │    │                 │
│ • Form UI       │    │ • REST API      │    │ • MusicGen      │
│ • Audio Player  │    │ • Pipeline      │    │ • CLAP          │
│ • A/B Testing   │    │ • Vector Search │    │ • LLM Agents    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Multi-Agent Workflow

1. **State Analysis Agent** - Analyzes stress levels and physical symptoms
2. **Emotion Recognition Agent** - Identifies emotions and regulation needs  
3. **Preference Analysis Agent** - Processes music preferences and constraints
4. **Requirement Integration Agent** - Combines analyses into unified requirements
5. **Prompt Generation Agent** - Creates optimized MusicGen prompts

## 🚀 Features

### 📝 Comprehensive Form System
- Multi-step form with progress tracking
- Stress, emotion, and preference assessment
- Real-time validation and guidance
- Responsive design for all devices

### 🎧 Advanced Audio Features
- Web Audio API integration
- High-quality music playback
- Play and replay
- Progress tracking and time display

### 🧪 A/B Testing Framework
- Blind music comparison testing
- Identify by email
- Statistical analysis capabilities
- User preference data collection

### 🤖 AI-Powered Recommendations
- LangGraph multi-agent pipeline
- MusicGen music synthesis
- CLAP audio encoding and similarity search
- Vector-based recommendation engine

## 📁 Project Structure

```
sleep-recommendation-system/
├── backend/                 # Flask API server
│   ├── src/
│   │   ├── api/            # REST API endpoints
│   │   ├── nodes/          # LangGraph agent nodes
│   │   ├── pipeline/       # Recommendation pipeline
│   │   ├── service/        # Business logic
│   │   └── state/          # State management
│   ├── data/               # Audio embeddings database
│   ├── dataset/            # Raw audio files
│   └── tests/              # Test suite
├── frontend/               # React TypeScript app
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API and audio services
│   │   └── types/          # TypeScript definitions
│   └── public/             # Static assets
└── docs/                   # Documentation
    ├── RecommendationSystem.md
    ├── FormDesign.md
    └── LangGraphGuild.md
```

## 🛠️ Technology Stack

### Backend
- **Framework**: Flask + Flask-RESTful
- **AI Pipeline**: LangGraph
- **Models**: MusicGen, CLAP, OpenAI GPT/Google Gemini
- **Audio Processing**: librosa, soundfile
- **Package Manager**: uv

### Frontend  
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite 7
- **UI Library**: Ant Design 5
- **Routing**: React Router DOM 7
- **Audio**: Web Audio API
- **HTTP Client**: Axios

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20.19+ or 22.12+
- uv (Python package manager)
- npm 10+

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   uv install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

4. **Start the server**:
   ```bash
   uv run main.py
   ```

   Server will be available at `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Configure API base URL if needed
   ```

4. **Start development server**:
   ```bash
   npm run dev
   ```

   App will be available at `http://localhost:3000`

## 📖 Usage

1. **Fill out the sleep assessment form** with your current stress levels, emotions, and music preferences
2. **Receive personalized recommendations** based on AI analysis of your inputs
3. **Listen to recommended music** with built-in audio controls
4. **Participate in A/B testing** to help improve the recommendation system

## 🧪 Testing

### Backend Tests
```bash
cd backend
uv run run_tests.py
```

### Frontend Build
```bash
cd frontend
npm run build
```

## 📚 Documentation

- [System Architecture](docs/RecommendationSystem.md) - Detailed system design and architecture
- [Form Design](docs/FormDesign.md) - User interface and form specifications  
- [LangGraph Guide](docs/LangGraphGuild.md) - Multi-agent workflow implementation

## 🔧 Configuration

### Required Environment Variables

**Backend (.env)**:
```bash
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key  
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=false
```

**Frontend (.env)**:
```bash
VITE_API_BASE_URL=http://localhost:5000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LangGraph for multi-agent workflow capabilities
- MusicGen for AI music generation
- CLAP for audio understanding
- Ant Design for UI components
- React and Flask communities
