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
