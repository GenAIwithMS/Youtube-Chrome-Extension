from fastapi import APIRouter
from datetime import datetime

health_router = APIRouter()
@health_router.get("/")
async def read_root():
    """Health check endpoint"""
    return {
        "message": "YouTube RAG Chat API is running",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@health_router.get("/health")
async def health_check():
    """Detailed health check"""
    from app.services.rag import embeddings, model
    return {
        "status": "healthy",
        "embeddings_loaded": embeddings is not None,
        "model_loaded": model is not None,
        "processed_videos": 0,
        "timestamp": datetime.now().isoformat()
    }
