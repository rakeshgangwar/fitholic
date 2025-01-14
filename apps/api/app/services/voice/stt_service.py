from typing import BinaryIO
import openai
from app.core.config import settings
import tempfile
import os

class STTService:
    """Whisper speech-to-text service"""
    
    def __init__(self):
        self.client = openai.Client(api_key=settings.OPENAI_API_KEY)
        
    def transcribe_audio(self, audio_data: bytes) -> str:
        """Convert speech to text using Whisper API"""
        temp_file_path = None
        try:
            # Save audio data to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Transcribe using Whisper
            with open(temp_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            return response
            
        except Exception as e:
            raise Exception(f"Speech recognition failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    def transcribe_stream(self, audio_stream: BinaryIO) -> str:
        """Transcribe streaming audio data"""
        try:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_stream,
                response_format="text"
            )
            return response
        except Exception as e:
            raise Exception(f"Stream transcription failed: {str(e)}")
