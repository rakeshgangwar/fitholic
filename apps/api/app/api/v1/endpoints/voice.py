from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.voice.voice_processor import VoiceProcessor
from app.services.workout_assistant.session_manager import WorkoutSessionManager
import tempfile
import os

router = APIRouter()
voice_processor = VoiceProcessor()
session_manager = WorkoutSessionManager()

@router.post("/command")
async def process_voice_command(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    audio_file: UploadFile = File(...),
) -> Any:
    """Process voice command and return response"""
    try:
        if not audio_file.filename or not audio_file.file:
            raise HTTPException(status_code=400, detail="No audio file provided")

        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(delete=False, suffix='.webm') as temp_audio:
            # Read the uploaded file in chunks
            while chunk := await audio_file.read(8192):
                temp_audio.write(chunk)
            temp_audio_path = temp_audio.name

        try:
            # Get or create workout session
            session = session_manager.get_or_create_session(str(current_user.id))
            
            # Get current exercise state
            current_exercise = None
            if session.exercises:
                exercise_keys = list(session.exercises.keys())
                if exercise_keys:
                    current_exercise = session.exercises[exercise_keys[session.current_exercise_index]]
            
            # Process voice command
            with open(temp_audio_path, 'rb') as audio_data:
                result = await voice_processor.process_voice_command(
                    audio_data.read(),
                    {
                        "user_id": str(current_user.id),
                        "session_id": session.session_id,
                        "current_exercise": current_exercise,
                        "template_id": session.template_id
                    }
                )
            
            # Update session state based on command
            command = result["command"]
            if command["type"] == "log_set" and current_exercise:
                session_manager.log_set(
                    session.session_id,
                    current_exercise.exercise_id,
                    command["weight"],
                    command["reps"]
                )
            elif command["type"] == "navigation":
                if command["action"] == "next":
                    session_manager.next_exercise(session.session_id)
                elif command["action"] == "previous":
                    session_manager.previous_exercise(session.session_id)
            
            return {
                "transcription": result["transcription"],
                "response_text": result["response_text"],
                "response_audio": result["response_audio"],
                "command_type": command["type"]
            }
            
        finally:
            # Clean up the temporary file
            os.unlink(temp_audio_path)
            
    except Exception as e:
        return {
            "error": str(e),
            "transcription": "",
            "response_text": "Sorry, I couldn't process that command. Please try again.",
            "response_audio": None
        }

@router.post("/session/start")
async def start_voice_session(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    template_id: str
) -> Any:
    """Start a new voice-assisted workout session"""
    try:
        session = session_manager.get_or_create_session(
            str(current_user.id),
            template_id
        )
        
        return {
            "session_id": session.session_id,
            "current_exercise": session_manager._get_current_exercise_state(session)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/end")
async def end_voice_session(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    session_id: str
) -> Any:
    """End voice-assisted workout session"""
    try:
        summary = session_manager.end_session(session_id)
        return summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
