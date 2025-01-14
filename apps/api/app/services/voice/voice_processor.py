from typing import Dict, Any
import openai
from app.core.config import settings
import tempfile
import os

class VoiceProcessor:
    def __init__(self):
        self.client = openai.Client(api_key=settings.OPENAI_API_KEY)
        self.elevenlabs_api_key = settings.ELEVENLABS_API_KEY

    async def process_voice_command(self, audio_data: bytes, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process voice command and return response"""
        temp_file_path = None
        try:
            # Save audio data to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            # Transcribe audio using Whisper
            with open(temp_file_path, 'rb') as audio_file:
                transcription = self.transcribe_audio(audio_file)

            # Process command using the transcription
            command = self.parse_command(transcription)

            # Generate response
            response_text = self.generate_response(command, context)

            # Convert response to speech
            response_audio = await self.text_to_speech(response_text)

            return {
                "transcription": transcription,
                "command": command,
                "response_text": response_text,
                "response_audio": response_audio
            }

        except Exception as e:
            raise Exception(f"Voice command processing failed: {str(e)}")
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def transcribe_audio(self, audio_file) -> str:
        """Transcribe audio using Whisper API"""
        try:
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            return response
        except Exception as e:
            raise Exception(f"Speech recognition failed: {str(e)}")

    def parse_command(self, transcription: str) -> Dict[str, Any]:
        """Parse transcribed text into a structured command"""
        # Example command parsing logic
        text = transcription.lower()
        
        # Check for set logging commands
        if "logged" in text or "log" in text:
            # Extract reps and weight
            import re
            reps_match = re.search(r'(\d+)\s*reps?', text)
            weight_match = re.search(r'(\d+)\s*(pounds?|lbs?)', text)
            
            if reps_match and weight_match:
                return {
                    "type": "log_set",
                    "reps": int(reps_match.group(1)),
                    "weight": int(weight_match.group(1))
                }
        
        # Check for navigation commands
        if "next" in text or "following" in text:
            return {
                "type": "navigation",
                "action": "next"
            }
        
        if "previous" in text or "back" in text:
            return {
                "type": "navigation",
                "action": "previous"
            }
        
        # Default to help command if no other matches
        return {
            "type": "help",
            "action": "show_help"
        }

    def generate_response(self, command: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate response text based on command and context"""
        if command["type"] == "log_set":
            return f"Logged {command['reps']} reps at {command['weight']} pounds."
        elif command["type"] == "navigation":
            return f"Moving to {command['action']} exercise."
        else:
            return "You can say commands like 'logged 10 reps at 100 pounds' or 'next exercise'."

    async def text_to_speech(self, text: str) -> str:
        """Convert text to speech using ElevenLabs API"""
        try:
            import aiohttp
            import base64
            
            url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }

            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        # Convert audio data to base64
                        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                        return audio_base64
                    else:
                        error_text = await response.text()
                        raise Exception(f"ElevenLabs API error: {error_text}")
                
        except Exception as e:
            raise Exception(f"Text-to-speech failed: {str(e)}")
