from fastapi import HTTPException
from youtube_transcript_api import TranscriptsDisabled, NoTranscriptFound
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Initialize embeddings model (load once for efficiency)
try:
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    logger.info("Embeddings model loaded successfully")
except Exception as e:
    logger.error(f"Failed to load embeddings model: {e}")
    embeddings = None

# Initialize LLM
try:
    model = ChatOpenAI(model_name="openai/gpt-oss-120b",base_url="https://api.canopywave.io/v1")
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
    - Provide Explaination when asked by user
    
    Transcript:
    {transcript}
    
    Question: {question}
    
    Answer:""",
    input_variables=["transcript", "question"]
)

def extract_transcript(video_id: str) -> str:
    """Extract transcript from YouTube video"""
    try:
        from app.services.transcript import fetch_transcript
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
    # try:
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
    try:
        if embeddings is None:
            logger.error("Embeddings model is not loaded")
            raise HTTPException(status_code=500, detail="Embeddings model not available")
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
