from fastapi import APIRouter, HTTPException
from app.schemas.video import VideoRequest, ChatRequest, ProcessResponse, ChatResponse
from app.services.rag import extract_transcript, create_vector_store, format_docs, model, prompt
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

video_router = APIRouter()

# Global storage for processed videos (in production, use a proper database)
processed_videos: Dict[str, Dict[str, Any]] = {}

@video_router.post("/process_video", response_model=ProcessResponse)
async def process_video(request: VideoRequest):
    """Process a YouTube video for RAG chat"""
    video_id = request.video_id.strip()
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Video ID is required")
    
    logger.info(f"Processing video: {video_id}")
    
    try:
        # Check if video is already processed
        if video_id in processed_videos:
            logger.info(f"Video {video_id} already processed")
            return ProcessResponse(
                message=f"Video {video_id} was already processed and is ready for chat",
                video_id=video_id,
                status="already_processed",
                timestamp=datetime.now().isoformat()
            )
        
        # Extract transcript
        transcript = extract_transcript(video_id)
        
        # if not transcript.strip():
        #     raise HTTPException(status_code=400, detail="Empty transcript extracted")
        
        # Create vector store
        vector_store = create_vector_store(transcript, video_id)
        
        # Create retriever
        retriever = vector_store.as_retriever(
            search_type="similarity", 
            search_kwargs={"k": 4}
        )
        
        # Create RAG chain
        parallel_chain = RunnableParallel({
            "transcript": retriever | RunnableLambda(format_docs),
            "question": RunnablePassthrough()
        })
        
        parser = StrOutputParser()
        main_chain = parallel_chain | prompt | model | parser
        
        # Store processed video data
        processed_videos[video_id] = {
            "vector_store": vector_store,
            "retriever": retriever,
            "chain": main_chain,
            "transcript_length": len(transcript),
            "processed_at": datetime.now().isoformat()
        }
        
        logger.info(f"Successfully processed video {video_id}")
        
        return ProcessResponse(
            message=f"Video {video_id} processed successfully and is ready for chat",
            video_id=video_id,
            status="processed",
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing video {video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@video_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with processed video content"""
    video_id = request.video_id.strip()
    query = request.query.strip()
    
    if not video_id:
        raise HTTPException(status_code=400, detail="Video ID is required")
    
    if not query:
        raise HTTPException(status_code=400, detail="Query is required")
    
    logger.info(f"Chat request for video {video_id}: {query}")
    
    try:
        # Check if video is processed
        if video_id not in processed_videos:
            raise HTTPException(
                status_code=404, 
                detail=f"Video {video_id} has not been processed. Please process it first."
            )
        
        # Get the RAG chain for this video
        video_data = processed_videos[video_id]
        chain = video_data["chain"]
        
        if model is None:
            raise HTTPException(status_code=500, detail="Language model not available")
        
        # Generate response
        response = chain.invoke(query)
        
        logger.info(f"Generated response for video {video_id}")
        
        return ChatResponse(
            response=response,
            video_id=video_id,
            query=query,
            timestamp=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating response for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")
    

@video_router.get("/videos")
async def list_processed_videos():
    """List all processed videos"""
    videos = []
    for video_id, data in processed_videos.items():
        videos.append({
            "video_id": video_id,
            "processed_at": data["processed_at"],
            "transcript_length": data["transcript_length"]
        })
    
    return {
        "processed_videos": videos,
        "count": len(videos),
        "timestamp": datetime.now().isoformat()
    }

@video_router.delete("/videos/{video_id}")
async def delete_processed_video(video_id: str):
    """Delete a processed video from memory"""
    if video_id not in processed_videos:
        raise HTTPException(status_code=404, detail="Video not found")
    
    del processed_videos[video_id]
    logger.info(f"Deleted processed video: {video_id}")
    
    return {
        "message": f"Video {video_id} deleted successfully",
        "timestamp": datetime.now().isoformat()
    }
