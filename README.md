# YouTube RAG Chat Project

A complete solution for chatting with YouTube video content using Retrieval-Augmented Generation (RAG) technology. This project consists of a FastAPI backend with advanced RAG pipeline and a Chrome extension frontend with a modern dark theme interface.

## 🚀 Features

### Backend (FastAPI)
- **Modular Architecture**: Clean separation with app factory pattern
- **Advanced RAG Pipeline**: FAISS vector store with HuggingFace embeddings (sentence-transformers/all-MiniLM-L6-v2)
- **YouTube Integration**: Multi-language transcript extraction (English, Hindi, Bengali, Chinese)
- **LLM Integration**: Powered by Canopy Wave API with gpt-oss-120b model
- **RESTful API**: Well-structured endpoints with Pydantic schemas
- **Smart Chunking**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
- **Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Configured for frontend integration

### Frontend (Chrome Extension)
- **🎯 Auto-Detection**: Automatically detects YouTube videos
- **🔄 Auto-Processing**: Processes videos automatically
- **💬 Dark Theme**: Modern chat interface matching the provided design
- **💾 Persistence**: Stores conversation history per video
- **🔵 Visual Feedback**: Status indicators and loading states
- **⚡ Real-time**: Instant responses from RAG backend

## 📁 Project Structure

```
youtube-rag-project/
├── backend/                          # FastAPI Backend
│   ├── app/                         # Main application package
│   │   ├── __init__.py             # App factory
│   │   ├── api/                    # API layer
│   │   │   ├── routes/             # API routes
│   │   │   │   ├── video.py        # Video processing & chat endpoints
│   │   │   │   └── health.py       # Health check endpoints
│   │   │   └── __init__.py
│   │   ├── schemas/                # Pydantic models
│   │   │   ├── video.py            # Request/Response schemas
│   │   │   └── __init__.py
│   │   ├── services/               # Business logic
│   │   │   ├── rag.py              # RAG pipeline & vector store
│   │   │   ├── transcript.py       # Transcript extraction
│   │   │   └── __init__.py
│   │   └── config/                 # Configuration
│   │       └── __init__.py
│   ├── main.py                     # Application entry point
│   ├── requirements.txt            # Python dependencies
│   ├── .env.example                # Environment variables template
│   ├── Get_transcript.py           # Legacy transcript utility
│   ├── youtube_downloader.py       # Video download utility
│   └── README.md                   # Backend documentation
├── frontend/                        # Chrome Extension
│   ├── youtube-rag-extension/      # Extension files
│   │   ├── manifest.json           # Extension manifest
│   │   ├── popup/                  # Chat interface
│   │   │   ├── popup.html          # Dark theme UI
│   │   │   ├── popup.js            # Chat functionality
│   │   │   ├── popupreal.js        # Chat logic
│   │   │   └── marked.min.js       # Markdown parser
│   │   ├── content/                # YouTube integration
│   │   │   ├── content.js          # Page integration
│   │   │   └── content.css         # Floating button styles
│   │   ├── background/             # Service worker
│   │   │   └── background.js       # Background tasks
│   │   └── icons/                  # Extension icons
│   │       ├── icon16.png
│   │       ├── icon48.png
│   │       ├── icon128.png
│   │       └── downlaod.png
│   └── README.md                   # Frontend documentation
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## 🛠️ Setup Instructions

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Start the server
python main.py
```

The backend will be available at `http://localhost:8000`

### 2. Frontend Setup

```bash
# The extension files are ready to load in Chrome
# No additional setup required
```

### 3. Chrome Extension Installation

1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode" (top right toggle)
3. Click "Load unpacked"
4. Select the `frontend/youtube-rag-extension` folder
5. The extension icon will appear in your Chrome toolbar

## 🎯 Usage

### Quick Start
1. **Start Backend**: Run the FastAPI server (`python backend/main.py`)
2. **Install Extension**: Load the extension in Chrome
3. **Open YouTube**: Navigate to any YouTube video
4. **Auto-Process**: The extension automatically processes the video
5. **Chat**: Click the extension icon and start chatting!

### Workflow
1. Extension detects YouTube video ID from current tab
2. Sends processing request to backend `/process_video` endpoint
3. Backend extracts transcript, chunks text, creates embeddings
4. User asks questions via chat interface
5. Backend retrieves relevant chunks and generates contextual answers
6. Conversation history persists per video in Chrome storage

## 🔧 API Endpoints

### Backend API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Detailed health status |
| `/process_video` | POST | Process YouTube video |
| `/chat` | POST | Chat with video content |
| `/videos` | GET | List processed videos |
| `/videos/{id}` | DELETE | Delete processed video |

### Example API Usage

```bash
# Process a video
curl -X POST "http://localhost:8000/process_video" \
     -H "Content-Type: application/json" \
     -d '{"video_id": "dQw4w9WgXcQ"}'

# Chat with the video
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"video_id": "dQw4w9WgXcQ", "query": "What is this video about?"}'
```

## 🎨 Interface Design

The Chrome extension features a modern dark theme that matches the provided screenshot:

- **Dark Background**: Clean dark interface (#1a1a1a)
- **Message Bubbles**: Rounded chat bubbles with proper alignment
- **Blue Accent**: Blue color scheme (#4a9eff) for user messages
- **Status Bar**: Real-time status updates
- **Loading States**: Smooth loading indicators
- **Auto-scroll**: Automatic scrolling to latest messages

## 🔑 Environment Variables

Create a `.env` file in the backend directory:

```env
# Required - Canopy Wave API Key for LLM
OPENAI_API_KEY=your_canopy_wave_api_key

# Optional
HUGGINGFACE_API_TOKEN=your_huggingface_token
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

## 📋 Requirements

### Backend Dependencies
- Python 3.8+
- FastAPI & Uvicorn
- LangChain (Community, Core, HuggingFace, OpenAI, Text Splitters)
- FAISS (CPU version)
- HuggingFace Transformers & Sentence Transformers
- PyTorch
- Canopy Wave API (via langchain-openai)
- YouTube Transcript API
- yt-dlp (for video downloads)
- Pydantic & python-dotenv

### Frontend Requirements
- Chrome browser (or Chromium-based)
- Developer mode enabled
- Local backend server running

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check if OPENAI_API_KEY is set in .env file |
| Module import errors | Run `pip install -r requirements.txt` |
| Extension not loading | Enable Developer mode in Chrome extensions |
| Video processing fails | Ensure video has available transcripts (English, Hindi, Bengali, or Chinese) |
| Chat not responding | Verify backend is running on http://localhost:8000 |
| CORS errors | Check backend CORS middleware configuration |
| Embeddings model download | First run downloads models automatically; requires internet |
| Large video processing slow | Normal for first-time processing; subsequent chats are fast |

## 🔄 RAG Pipeline

The system uses an advanced RAG pipeline with modular architecture:

1. **Transcript Extraction** ([services/transcript.py](backend/app/services/transcript.py))
   - Fetches video transcripts using YouTube Transcript API
   - Supports multiple languages: English, Hindi, Bengali, Chinese
   - Automatic text cleaning and formatting

2. **Text Chunking** ([services/transcript.py](backend/app/services/transcript.py))
   - Uses langchain-text-splitters package
   - RecursiveCharacterTextSplitter configuration
   - Chunk size: 1000 characters
   - Chunk overlap: 200 characters
   - Creates LangChain Document objects with metadata

3. **Embeddings** ([services/rag.py](backend/app/services/rag.py))
   - Model: sentence-transformers/all-MiniLM-L6-v2
   - HuggingFace embeddings integration
   - Efficient vector representation

4. **Vector Store** ([services/rag.py](backend/app/services/rag.py))
   - FAISS for high-performance similarity search
   - In-memory storage for fast retrieval
   - Persistent across video processing sessions

5. **Retrieval** ([api/routes/video.py](backend/app/api/routes/video.py))
   - Similarity-based search
   - Retrieves top-4 most relevant chunks
   - Context-aware document formatting

6. **Generation** ([services/rag.py](backend/app/services/rag.py))
   - LLM: Canopy Wave's gpt-oss-120b (via OpenAI-compatible API)
   - Base URL: https://api.canopywave.io/v1
   - Custom prompt template for video Q&A
   - Streaming support via RunnableParallel

## 🚀 Production Deployment

For production use:

1. **Backend Deployment**
   - Deploy to cloud service (AWS, GCP, Azure, Heroku)
   - Set production environment variables
   - Replace in-memory `processed_videos` dict with persistent database (Redis, PostgreSQL)
   - Implement authentication & authorization (JWT, OAuth)
   - Add rate limiting and request throttling
   - Use production ASGI server (Gunicorn with Uvicorn workers)

2. **Security**
   - Secure OPENAI_API_KEY (Canopy Wave) and other credentials
   - Update CORS origins to specific domains
   - Implement API key authentication for endpoints
   - Add HTTPS/TLS certificates

3. **Monitoring**
   - Set up logging aggregation (ELK, CloudWatch)
   - Implement health checks and uptime monitoring
   - Track API usage and performance metrics

4. **Extension Updates**
   - Update API_BASE_URL in popup.js to production URL
   - Publish to Chrome Web Store
   - Update manifest version and permissions

5. **Scalability**
   - Implement caching for frequently accessed videos
   - Use message queues for video processing (Celery, RabbitMQ)
   - Load balancing for multiple backend instances

## 📝 License

This project is provided as-is for educational and development purposes.

## 🏗️ Architecture

### Backend Architecture
```
app/
├── __init__.py          # App factory with CORS & router setup
├── api/routes/          # API endpoints (video, health)
├── schemas/             # Pydantic request/response models
├── services/            # Business logic (RAG, transcript)
└── config/              # Configuration management
```

### Tech Stack

**Backend:**
- **Framework**: FastAPI (async Python web framework)
- **LLM**: Canopy Wave API (gpt-oss-120b model via OpenAI-compatible endpoint)
- **Embeddings**: HuggingFace sentence-transformers
- **Vector DB**: FAISS (Facebook AI Similarity Search)
- **Orchestration**: LangChain (RAG pipeline)
- **Transcript**: YouTube Transcript API

**Frontend:**
- **Platform**: Chrome Extension (Manifest V3)
- **UI**: Vanilla JavaScript with dark theme
- **Storage**: Chrome Storage API
- **Markdown**: Marked.js for rendering

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Use type hints in Python functions
- Write descriptive commit messages
- Update README for significant changes
- Test both backend API and extension thoroughly

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the individual README files in backend/ and frontend/
- Ensure all dependencies are properly installed
- Verify API keys are correctly configured

