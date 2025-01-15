from typing import Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.services.voice.voice_processor import VoiceProcessor
from app.services.workout_assistant.session_manager import WorkoutSessionManager
from app.crud.workouts import workout_logs
import tempfile
import os
from datetime import datetime

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
            # Get ongoing workout log
            ongoing_log = workout_logs.get_ongoing_log(db, current_user.id)
            if not ongoing_log:
                raise HTTPException(status_code=400, detail="No active workout session found")
            
            # Find current exercise (first incomplete exercise)
            current_exercise = next(
                (ex for ex in ongoing_log.exercises if not ex.get("completed", False)),
                None
            )
            
            # Process voice command
            with open(temp_audio_path, 'rb') as audio_data:
                result = await voice_processor.process_voice_command(
                    audio_data.read(),
                    {
                        "user_id": str(current_user.id),
                        "log_id": str(ongoing_log.log_id),
                        "current_exercise": current_exercise["exercise_id"] if current_exercise else None,
                        "template_id": ongoing_log.template_id
                    }
                )
            
            # Update workout log based on command
            command = result["command"]
            if command["type"] == "log_set" and current_exercise:
                current_exercise["sets"].append({
                    "weight": command["weight"],
                    "reps": command["reps"],
                    "completed": True
                })
                # Check if all sets are completed
                if len(current_exercise["sets"]) >= current_exercise.get("target_sets", 0):
                    current_exercise["completed"] = True
                workout_logs.update(
                    db,
                    db_obj=ongoing_log,
                    obj_in={"exercises": ongoing_log.exercises}
                )
            elif command["type"] == "navigation":
                current_idx = next(
                    (i for i, ex in enumerate(ongoing_log.exercises) if not ex.get("completed", False)),
                    -1
                )
                if command["action"] == "next" and current_idx < len(ongoing_log.exercises) - 1:
                    if current_exercise:
                        current_exercise["completed"] = True
                elif command["action"] == "previous" and current_idx > 0:
                    ongoing_log.exercises[current_idx - 1]["completed"] = False
                elif command["action"] == "skip" and current_idx < len(ongoing_log.exercises) - 1:
                    if current_exercise:
                        current_exercise["completed"] = True
                workout_logs.update(
                    db,
                    db_obj=ongoing_log,
                    obj_in={"exercises": ongoing_log.exercises}
                )
            elif command["type"] == "complete":
                workout_logs.update(
                    db,
                    db_obj=ongoing_log,
                    obj_in={
                        "status": "completed",
                        "end_time": datetime.now(),
                        "notes": command.get("notes", "")
                    }
                )
            
            return {
                "transcription": result["transcription"],
                "response_text": result["response_text"],
                "response_audio": result["response_audio"],
                "command_type": command["type"],
                "command_parameters": command
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
        # Check for existing ongoing session
        ongoing_log = workout_logs.get_ongoing_log(db, current_user.id)
        if ongoing_log:
            return {"log_id": str(ongoing_log.log_id)}

        # Create new workout log
        workout_log = workout_logs.create_from_template(
            db,
            user_id=current_user.id,
            template_id=template_id
        )
        return {"log_id": str(workout_log.log_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/session/end")
async def end_voice_session(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """End voice-assisted workout session"""
    try:
        ongoing_log = workout_logs.get_ongoing_log(db, current_user.id)
        if not ongoing_log:
            raise HTTPException(status_code=400, detail="No active workout session found")
            
        workout_logs.update(
            db,
            db_obj=ongoing_log,
            obj_in={
                "status": "completed",
                "end_time": datetime.now()
            }
        )
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
