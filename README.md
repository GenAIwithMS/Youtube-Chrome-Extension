# YouTube RAG Chat Project

A complete solution for chatting with YouTube video content using Retrieval-Augmented Generation (RAG) technology. This project consists of a FastAPI backend with advanced RAG pipeline and a Chrome extension frontend with a modern dark theme interface.

## 🚀 Features

### Backend (FastAPI)
- **Advanced RAG Pipeline**: Uses FAISS vector store and HuggingFace embeddings
- **YouTube Integration**: Automatic transcript extraction and processing
- **LLM Integration**: Powered by Groq's gemma2-9b-it model
- **RESTful API**: Clean, documented endpoints
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
│   ├── main.py                      # Main FastAPI application
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment variables template
│   └── README.md                    # Backend documentation
├── frontend/                        # Chrome Extension
│   ├── youtube-rag-extension/       # Extension files
│   │   ├── manifest.json           # Extension manifest
│   │   ├── popup/                  # Chat interface
│   │   │   ├── popup.html          # Dark theme UI
│   │   │   └── popup.js            # Chat functionality
│   │   ├── content/                # YouTube integration
│   │   │   ├── content.js          # Page integration
│   │   │   └── content.css         # Floating button styles
│   │   ├── background/             # Service worker
│   │   │   └── background.js       # Background tasks
│   │   └── icons/                  # Extension icons
│   │       ├── icon16.png
│   │       ├── icon48.png
│   │       └── icon128.png
│   └── README.md                    # Frontend documentation
└── README.md                        # This file
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
# Edit .env and add your GROQ_API_KEY

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

1. **Start Backend**: Run the FastAPI server (`python backend/main.py`)
2. **Install Extension**: Load the extension in Chrome
3. **Open YouTube**: Navigate to any YouTube video
4. **Auto-Process**: The extension automatically processes the video
5. **Chat**: Click the extension icon and start chatting!

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
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
HUGGINGFACE_API_TOKEN=your_huggingface_token_here
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

## 📋 Requirements

### Backend Dependencies
- Python 3.8+
- FastAPI
- LangChain
- FAISS
- HuggingFace Transformers
- Groq API access
- YouTube Transcript API

### Frontend Requirements
- Chrome browser (or Chromium-based)
- Developer mode enabled
- Local backend server running

## 🚨 Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check if GROQ_API_KEY is set in .env |
| Extension not loading | Enable Developer mode in Chrome |
| Video processing fails | Ensure video has English captions |
| Chat not responding | Verify backend is running on port 8000 |
| CORS errors | Check backend CORS configuration |

## 🔄 RAG Pipeline

The system uses an advanced RAG pipeline:

1. **Transcript Extraction**: YouTube Transcript API
2. **Text Chunking**: RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
3. **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
4. **Vector Store**: FAISS for similarity search
5. **Retrieval**: Top-4 similar chunks
6. **Generation**: Groq's gemma2-9b-it model

## 🚀 Production Deployment

For production use:

1. **Backend**: Deploy to cloud service (AWS, GCP, Azure)
2. **Environment**: Use production environment variables
3. **Database**: Replace in-memory storage with persistent database
4. **Security**: Implement authentication and rate limiting
5. **Extension**: Update API_BASE_URL in popup.js

## 📝 License

This project is provided as-is for educational and development purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the individual README files in backend/ and frontend/
- Ensure all dependencies are properly installed
- Verify API keys are correctly configured

