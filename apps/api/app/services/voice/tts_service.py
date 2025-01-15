"""
Text-to-Speech Service Module

This module handles the conversion of text responses to audio using ElevenLabs' TTS model.

Components:
1. TTSService: Main class for speech synthesis
2. Voice Configuration: Settings for voice characteristics
3. Audio Processing: Post-processing and format conversion

Flow:
1. Text response is received from command processor
2. Voice and style parameters are selected
3. Audio is generated using TTS model
4. Audio is post-processed and returned to client

TODO:
1. Add support for multiple voices and accents
2. Implement emotion-aware speech synthesis
3. Add support for SSML markup for better prosody
4. Implement audio caching for common responses
5. Add support for multiple audio formats
6. Implement streaming audio response
7. Add voice customization options
8. Implement fallback TTS service
9. Add proper error handling for synthesis issues
10. Implement adaptive speaking rate based on context
"""

from typing import Optional
import httpx
from app.core.config import settings

class TTSService:
    """ElevenLabs text-to-speech service"""
    
    def __init__(self):
        self.api_key = settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Default voice ID
        
    async def synthesize_speech(
        self,
        text: str,
        voice_id: Optional[str] = None
    ) -> bytes:
        """Convert text to speech using ElevenLabs API"""
        try:
            url = f"{self.base_url}/text-to-speech/{voice_id or self.default_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.75,
                    "similarity_boost": 0.75
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                return response.content
                
        except httpx.HTTPError as e:
            raise Exception(f"TTS API error: {str(e)}")
        except Exception as e:
            raise Exception(f"TTS generation failed: {str(e)}")
