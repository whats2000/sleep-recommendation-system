# Sleep Recommendation System - Backend

A LangGraph-based multi-agent recommendation system for personalized sleep music recommendations.

## Overview

This system implements the architecture described in the documentation, featuring:

- **LangGraph Multi-Agent Pipeline**: 5 specialized agents for comprehensive analysis
- **MusicGen Integration**: AI-powered music generation for reference audio
- **CLAP Audio Encoding**: Vector embeddings for similarity search
- **Vector Search Engine**: Cosine similarity-based music recommendations
- **Flask REST API**: Easy integration with frontend applications

## Architecture

```
User Form → LangGraph Pipeline → MusicGen → CLAP Encoding → Vector Search → Recommendations
```

### LangGraph Agents

1. **State Analysis Agent**: Analyzes stress levels and physical symptoms
2. **Emotion Recognition Agent**: Identifies emotions and regulation needs
3. **Preference Analysis Agent**: Processes music preferences and constraints
4. **Requirement Integration Agent**: Combines all analyses into unified requirements
5. **Prompt Generation Agent**: Creates optimized MusicGen prompts

## Installation

### Prerequisites

- Python 3.11+
- uv (Python package manager)
- CUDA-compatible GPU (optional, for MusicGen)

### Setup

1. **Install dependencies**:
   ```bash
   cd backend
   uv install
   ```

2. **Set up environment variables**:
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Add your API keys
   OPENAI_API_KEY=your_openai_key_here
   # OR
   GOOGLE_API_KEY=your_google_key_here
   ```

3. **Prepare audio database** (optional):
   ```bash
   # Place your audio files in backend/dataset/
   # Run encoding script to create embeddings
   uv run python src/utils/encode_audio.py
   ```

## Usage

### Running the API Server

```bash
cd backend
uv run python src/main.py
```

The server will start on `http://localhost:5000`

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Service Status
```bash
GET /status
```

#### Get Recommendations
```bash
POST /api/recommendations
Content-Type: application/json

{
  "stress_level": "中度壓力",
  "physical_symptoms": ["頭腦過度活躍", "肌肉緊繃"],
  "emotional_state": "焦慮",
  "sleep_goal": "快速入眠",
  "sound_preferences": ["樂器聲（鋼琴、古典、弦樂）"],
  "rhythm_preference": "超慢（冥想般，幾乎無節奏）",
  "sound_sensitivities": ["高頻刺耳聲"],
  "playback_mode": "逐漸淡出（10~20分鐘入睡）",
  "guided_voice": "否，只需要純音樂",
  "sleep_theme": "平靜如水（穩定神經）"
}
```

#### Pipeline Status
```bash
GET /api/pipeline/status/{session_id}
```

### Testing

Run the comprehensive test suite:

```bash
cd backend
uv run python run_tests.py
```

Or run individual test files:

```bash
# Test the LangGraph pipeline
uv run python tests/test_pipeline.py

# Test the API endpoints
uv run python tests/test_api.py
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: OpenAI API key for LLM agents
- `GOOGLE_API_KEY`: Google API key for Gemini (alternative to OpenAI)
- `FLASK_HOST`: Server host (default: 0.0.0.0)
- `FLASK_PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Debug mode (default: False)

### Model Configuration

The system uses these models by default:
- **LLM**: OpenAI GPT-4o-mini or Google Gemini-2.0-flash
- **MusicGen**: facebook/musicgen-small
- **CLAP**: laion/clap-htsat-unfused

Models are automatically downloaded on first use.

## Development

### Project Structure

```
backend/
├── src/
│   ├── api/           # Flask API endpoints
│   ├── nodes/         # LangGraph agent nodes
│   ├── pipeline/      # LangGraph pipeline
│   ├── service/       # Business logic services
│   ├── state/         # State management
│   └── utils/         # Utility functions
├── tests/             # Test suite
├── data/              # Audio embeddings database
├── dataset/           # Raw audio files
└── generated_audio/   # Generated reference audio
```

### Adding New Agents

1. Create a new agent file in `src/nodes/`
2. Implement the agent function following the pattern
3. Add the agent to `src/nodes/__init__.py`
4. Update the pipeline in `src/pipeline/recommendation_pipeline.py`

### Extending the API

1. Add new endpoints in `src/api/app.py`
2. Create corresponding service methods
3. Add tests in `tests/test_api.py`

## Troubleshooting

### Common Issues

1. **Model Loading Errors**: Ensure sufficient GPU memory or use CPU mode
2. **API Key Issues**: Verify environment variables are set correctly
3. **Audio Encoding Errors**: Check audio file formats and paths
4. **Memory Issues**: Reduce batch sizes or use smaller models

### Mock Mode

The system includes mock implementations for development:
- Mock LLM responses when no API key is provided
- Mock audio generation when MusicGen is unavailable
- Mock embeddings for testing without audio database

### Logs

Check console output for detailed processing information and error messages.

## Performance

### Optimization Tips

1. **GPU Usage**: Enable CUDA for faster MusicGen and CLAP processing
2. **Caching**: Enable checkpointing for pipeline state persistence
3. **Batch Processing**: Process multiple requests together when possible
4. **Model Selection**: Use smaller models for faster inference

### Benchmarks

Typical processing times (CPU):
- LangGraph Pipeline: 10-30 seconds
- MusicGen Generation: 30-60 seconds
- CLAP Encoding: 5-10 seconds
- Vector Search: <1 second

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

See the LICENSE file in the project root.
