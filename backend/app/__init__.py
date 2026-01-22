from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api.routes import video_router, health_router
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
def create_app():
    app = FastAPI(
        title="YouTube RAG Chat API",
        description="A FastAPI backend for chatting with YouTube video content using RAG",
        version="1.0.0"
    )

    # CORS middleware for allowing frontend requests
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(video_router, tags=["videos"])
    app.include_router(health_router, tags=["health"])

    return app


