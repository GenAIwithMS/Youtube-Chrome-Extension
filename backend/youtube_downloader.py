import yt_dlp
import os
from pathlib import Path

# def download_video(url: str, output_path: str = "downloads", progress_hook=None) -> dict:
#     # ... (your existing code)
#     ydl_opts = {
#         'format': 'best[height<=720]',
#         'outtmpl': f'{output_path}/%(title)s.%(ext)s',
#         'progress_hooks': [progress_hook] if progress_hook else [], # <-- ADD THIS
#     }
#     # ... (the rest of the function)


def download_video(url: str, output_path: str = "downloads",progress_hook=None) -> dict:
    """
    Download video from YouTube URL
    
    Args:
        url (str): YouTube video URL
        output_path (str): Directory to save the video
        
    Returns:
        dict: Status and file information
    """
    try:
        # Create download directory if it doesn't exist
        Path(output_path).mkdir(exist_ok=True)
        
        # yt-dlp options for video download
        ydl_opts = {
            'format': 'best[height<=720]',  # 720p quality
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'progress_hooks': [progress_hook] if progress_hook else [],
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Extract video info
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Unknown')
            
            # Download the video
            ydl.download([url])
            
            return {
                'status': 'success',
                'title': title,
                'file_path': f"{output_path}/{title}.mp4",
                'type': 'video'
            }
            
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
    
# def download_audio(url: str, output_path: str = "downloads", progress_hook=None) -> dict:
#     # ... (your existing code)
#     ydl_opts = {
#         'format': 'bestaudio/best',
#         'outtmpl': f'{output_path}/%(title)s.%(ext)s',
#         'postprocessors': [{
#             'key': 'FFmpegExtractAudio',
#             'preferredcodec': 'mp3',
#             'preferredquality': '192',
#         }],
#         'progress_hooks': [progress_hook] if progress_hook else [], # <-- ADD THIS
#     }

def download_audio(url: str, output_path: str = "downloads", progress_hook=None) -> dict:
    """
    Download audio from YouTube URL
    
    Args:
        url (str): YouTube video URL
        output_path (str): Directory to save the audio
        
    Returns:
        dict: Status and file information
    """
    try:
        # Create download directory if it doesn't exist
        Path(output_path).mkdir(exist_ok=True)
        
        # First try with FFmpeg conversion to MP3
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [progress_hook] if progress_hook else [],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video info
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                
                # Download and convert to audio
                ydl.download([url])
                
                return {
                    'status': 'success',
                    'title': title,
                    'file_path': f"{output_path}/{title}.mp3",
                    'type': 'audio'
                }
        
        except Exception as ffmpeg_error:
            # Fallback: Download best audio format without conversion
            print("FFmpeg not found, downloading best audio format without conversion...")
            ydl_opts_fallback = {
                'format': 'bestaudio/best',
                'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            }
            
            with yt_dlp.YoutubeDL(ydl_opts_fallback) as ydl:
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                ext = info.get('ext', 'webm')  # Usually webm or m4a
                
                ydl.download([url])
                
                return {
                    'status': 'success',
                    'title': title,
                    'file_path': f"{output_path}/{title}.{ext}",
                    'type': 'audio',
                    'note': 'Downloaded in original format (FFmpeg not available for MP3 conversion)'
                }
            
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

# # Test function
# def test_download():
#     """Test the download functions"""
#     test_url = "https://youtu.be/0OgUxSShtKk?si=pVHRMO1coj2ndNw7"  # Rick Roll for testing
    
#     print("Testing video download...")
#     result = download_video(test_url)
#     print(f"Video download result: {result}")
    
#     print("\nTesting audio download...")
#     result = download_audio(test_url)
#     print(f"Audio download result: {result}")

# if __name__ == "__main__":
#     test_download()