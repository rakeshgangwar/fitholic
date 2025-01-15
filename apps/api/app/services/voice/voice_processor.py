"""
Voice Processor Module

This module orchestrates the entire voice interaction flow, coordinating between STT, Command Processing, and TTS.

Components:
1. VoiceProcessor: Main orchestrator class
2. Service Integration: Manages STT, Command Processing, and TTS services
3. Error Handling: Manages failures in the voice processing pipeline

Flow:
1. Audio input is received from client
2. STT converts audio to text
3. Command processor interprets and executes command
4. TTS converts response to audio
5. Audio response is returned to client

Current Implementation Gaps:
1. Error Handling:
   - No proper recovery from service failures
   - Missing fallback mechanisms
   - Incomplete error reporting to client

2. State Management:
   - No persistence between commands
   - Missing context from previous interactions
   - No user preferences consideration

3. Performance:
   - Sequential processing might be slow
   - No caching of common operations
   - No optimization for gym environment

4. User Experience:
   - No real-time feedback
   - Missing progress indicators
   - No handling of background noise

TODO:
1. Implement proper error recovery in service chain
2. Add state persistence between commands
3. Implement parallel processing where possible
4. Add real-time feedback mechanisms
5. Implement proper logging and monitoring
6. Add support for offline fallback
7. Implement user preference handling
8. Add support for multi-turn conversations
9. Implement proper retry mechanisms
10. Add analytics for voice command usage
"""

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
            result = await self.command_processor.process_voice_command(transcription, context)

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
