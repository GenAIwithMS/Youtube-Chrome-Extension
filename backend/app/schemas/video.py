from pydantic import BaseModel
from typing import Optional


# Pydantic models for request/response
class DownloadRequest(BaseModel):
    video_id: str
    download_type: str  # "video" or "audio"
    output_path: Optional[str] = "downloads"

class DownloadResponse(BaseModel):
    status: str
    title: Optional[str] = None
    file_path: Optional[str] = None
    download_type: str
    error: Optional[str] = None
    timestamp: str


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
