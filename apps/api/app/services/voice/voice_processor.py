from typing import Dict, Any
import base64
from .stt_service import STTService
from .tts_service import TTSService
from .command_processor import CommandProcessor

class VoiceProcessor:
    def __init__(self):
        self.stt_service = STTService()
        self.tts_service = TTSService()
        self.command_processor = CommandProcessor()

    async def process_voice_command(self, audio_data: bytes, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process voice command and return response"""
        try:
            # Convert speech to text
            transcription = self.stt_service.transcribe_audio(audio_data)

            # Process command
            result = await self.command_processor.process_command(transcription, context)

            # Generate speech response
            audio_data = await self.tts_service.synthesize_speech(result["response_text"])
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            return {
                "transcription": transcription,
                "command": result["command"],
                "response_text": result["response_text"],
                "response_audio": audio_base64,
                "success": result["success"]
            }

        except Exception as e:
            raise Exception(f"Voice command processing failed: {str(e)}")
