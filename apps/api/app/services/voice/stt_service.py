import os
from typing import BinaryIO
import openai
from app.core.config import settings

class STTService:
    """Whisper speech-to-text service"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        openai.api_key = self.api_key
        
    async def transcribe_audio(self, audio_data: bytes) -> str:
        """Convert speech to text using Whisper API"""
        try:
            # Save audio data to a temporary file
            temp_path = "/tmp/audio_input.wav"
            with open(temp_path, "wb") as f:
                f.write(audio_data)
            
            # Transcribe using Whisper
            with open(temp_path, "rb") as audio_file:
                transcript = await openai.Audio.atranscribe(
                    "whisper-1",
                    audio_file
                )
            
            # Clean up
            os.remove(temp_path)
            
            return transcript.text
            
        except Exception as e:
            raise Exception(f"Speech recognition failed: {str(e)}")
        
    async def transcribe_stream(self, audio_stream: BinaryIO) -> str:
        """Transcribe streaming audio data"""
        try:
            transcript = await openai.Audio.atranscribe(
                "whisper-1",
                audio_stream
            )
            return transcript.text
        except Exception as e:
            raise Exception(f"Stream transcription failed: {str(e)}")
