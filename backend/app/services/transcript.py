from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


def text_splitter(docs):

    # print(docs)

    splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
            )
            
    chunks = splitter.split_text(docs)

    preprocessed_docs = []
    for chunk in chunks:
        preprocessed_docs.append(Document(page_content=chunk, metadata={}))
    return preprocessed_docs


        

def fetch_transcript(video_id: str):

    yt_transcript = YouTubeTranscriptApi()
    transcript_list = yt_transcript.fetch(video_id=video_id, languages=["en", "hi","bn","zh"])

    items = []
    for transcript in transcript_list:
            # Clean up transcript text
        text = transcript.text.replace("\n", " ").strip()
        if text:  # Only add non-empty text
            items.append(text)

    docs = " ".join(items)
    chunked_data = text_splitter(docs)
    return chunked_data
