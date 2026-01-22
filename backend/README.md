# YouTube RAG Chat Backend

A FastAPI backend that enables chatting with YouTube video content using Retrieval-Augmented Generation (RAG).

## Features

- **YouTube Transcript Extraction**: Automatically fetches video transcripts
- **RAG Pipeline**: Uses FAISS vector store and HuggingFace embeddings
- **LLM Integration**: Powered by Groq's gemma2-9b-it model
- **RESTful API**: Clean FastAPI endpoints for video processing and chat
- **Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Configured for frontend integration

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Required:
- `GROQ_API_KEY`: Your Groq API key for the language model

### 3. Run the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health status

### Video Processing
- `POST /process_video` - Process a YouTube video for RAG chat
  ```json
  {
    "video_id": "dQw4w9WgXcQ"
  }
  ```

### Chat
- `POST /chat` - Chat with processed video content
  ```json
  {
    "video_id": "dQw4w9WgXcQ",
    "query": "What is this video about?"
  }
  ```

### Video Management
- `GET /videos` - List all processed videos
- `DELETE /videos/{video_id}` - Delete a processed video

## RAG Pipeline

1. **Transcript Extraction**: Uses `youtube-transcript-api` to fetch video transcripts
2. **Text Chunking**: Splits transcript into overlapping chunks using `RecursiveCharacterTextSplitter`
3. **Embeddings**: Creates vector embeddings using `sentence-transformers/all-MiniLM-L6-v2`
4. **Vector Store**: Stores embeddings in FAISS for similarity search
5. **Retrieval**: Finds relevant chunks based on user queries
6. **Generation**: Uses Groq's gemma2-9b-it model to generate responses

## Error Handling

The API handles various error scenarios:
- Invalid video IDs
- Disabled transcripts
- Missing transcripts
- API rate limits
- Model failures

## Logging

Comprehensive logging is configured to track:
- Video processing status
- API requests and responses
- Error conditions
- Performance metrics

## Development

### Running in Development Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Testing the API

You can test the API using curl:

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

## Production Deployment

For production deployment:

1. Set proper environment variables
2. Use a production WSGI server
3. Configure proper CORS origins
4. Set up proper logging
5. Use a persistent database instead of in-memory storage
6. Implement authentication and rate limiting

## Dependencies

- **FastAPI**: Web framework
- **LangChain**: RAG pipeline framework
- **FAISS**: Vector similarity search
- **HuggingFace**: Embeddings and transformers
- **Groq**: Language model API
- **YouTube Transcript API**: Video transcript extraction

