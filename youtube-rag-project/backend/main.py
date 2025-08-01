from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
from datetime import datetime

# RAG Pipeline imports
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from Get_transcript import fetch_transcript

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
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

# Pydantic models for request/response
class VideoRequest(BaseModel):
    video_id: str

class ChatRequest(BaseModel):
    video_id: str
    query: str

class ProcessResponse(BaseModel):
    message: str
    video_id: str
    status: str
    timestamp: str

class ChatResponse(BaseModel):
    response: str
    video_id: str
    query: str
    timestamp: str

# Global storage for processed videos (in production, use a proper database)
processed_videos: Dict[str, Dict[str, Any]] = {}

# Initialize embeddings model (load once for efficiency)
try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    logger.info("Embeddings model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load embeddings model: {e}")
    embeddings = None

# Initialize LLM
try:
    model = ChatGroq(model="gemma2-9b-it", temperature=0.2)
    logger.info("ChatGroq model initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize ChatGroq model: {e}")
    model = None

# Prompt template
prompt = PromptTemplate(
    template="""You are a helpful assistant that answers questions based on YouTube video transcripts. 
    
    Instructions:
    - Provide accurate answers based only on the given transcript
    - If the transcript doesn't contain relevant information, say so clearly
    - Include specific details and examples from the video when possible
    - Be conversational and helpful
    - If asked about timestamps, mention that you can reference general sections but not exact times
    
    Transcript:
    {transcript}
    
    Question: {question}
    
    Answer:""",
    input_variables=["transcript", "question"]
)

def extract_transcript(video_id: str) -> str:
    """Extract transcript from YouTube video"""
    try:
        docs = fetch_transcript(video_id)
        return docs
        
    except TranscriptsDisabled:
        logger.error(f"Transcripts disabled for video {video_id}")
        raise HTTPException(status_code=400, detail="Transcripts are disabled for this video")
    except NoTranscriptFound:
        logger.error(f"No transcript found for video {video_id}")
        raise HTTPException(status_code=404, detail="No transcript found for this video")
    except Exception as e:
        logger.error(f"Error extracting transcript for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to extract transcript: {str(e)}")

def create_vector_store(docs: str, video_id: str) -> FAISS:
    """Create FAISS vector store from documents"""
    try:
        # Split documents into chunks
        # splitter = RecursiveCharacterTextSplitter(
        #     chunk_size=1000,
        #     chunk_overlap=200,
        #     length_function=len,
        # )
        
        # chunks = splitter.create_documents([docs])
        # logger.info(f"Created {len(chunks)} chunks for video {video_id}")
        
        # # Create vector store
        # if embeddings is None:
        #     raise HTTPException(status_code=500, detail="Embeddings model not available")
            
        vector_store = FAISS.from_documents(docs, embedding=embeddings)
        logger.info(f"Successfully created vector store for video {video_id}")
        return vector_store
        
    except Exception as e:
        logger.error(f"Error creating vector store for video {video_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create vector store: {str(e)}")

def format_docs(retrieved_docs):
    """Format retrieved documents for prompt"""
    context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
    return context_text

@app.get("/")
async def read_root():
    """Health check endpoint"""
    return {
        "message": "YouTube RAG Chat API is running",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "embeddings_loaded": embeddings is not None,
        "model_loaded": model is not None,
        "processed_videos": len(processed_videos),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/process_video", response_model=ProcessResponse)
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

@app.post("/chat", response_model=ChatResponse)
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

@app.get("/videos")
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

@app.delete("/videos/{video_id}")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

