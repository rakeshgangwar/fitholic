from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class WorkoutSet(BaseModel):
    """Model for a single set in a workout"""
    weight: float
    reps: int
    completed_at: datetime

class ExerciseProgress(BaseModel):
    """Model for tracking progress of an exercise"""
    exercise_id: str
    sets_completed: list[WorkoutSet]
    target_sets: int
    target_reps: int
    rest_duration: int

class WorkoutSession(BaseModel):
    """Model for an active workout session"""
    session_id: str
    user_id: str
    template_id: Optional[str]
    start_time: datetime
    current_exercise_index: int
    exercises: Dict[str, ExerciseProgress]
    notes: str = ""

class WorkoutSessionManager:
    """Manage active workout sessions"""
    
    def __init__(self):
        self.active_sessions: Dict[str, WorkoutSession] = {}
        
    def get_or_create_session(
        self,
        user_id: str,
        template_id: Optional[str] = None
    ) -> WorkoutSession:
        """Get existing session or create new one"""
        # Check for existing session
        for session in self.active_sessions.values():
            if session.user_id == user_id:
                return session
        
        # Create new session
        session_id = f"ws_{datetime.now().strftime('%Y%m%d%H%M%S')}_{user_id}"
        session = WorkoutSession(
            session_id=session_id,
            user_id=user_id,
            template_id=template_id,
            start_time=datetime.now(),
            current_exercise_index=0,
            exercises={}
        )
        
        self.active_sessions[session_id] = session
        return session
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End workout session and return summary"""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        summary = self._generate_session_summary(session)
        del self.active_sessions[session_id]
        return summary
    
    def log_set(
        self,
        session_id: str,
        exercise_id: str,
        weight: float,
        reps: int
    ) -> None:
        """Log a completed set"""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        exercise = session.exercises.get(exercise_id)
        if not exercise:
            raise ValueError(f"Exercise {exercise_id} not found in session")
            
        set_data = WorkoutSet(
            weight=weight,
            reps=reps,
            completed_at=datetime.now()
        )
        
        exercise.sets_completed.append(set_data)
    
    def next_exercise(self, session_id: str) -> Dict[str, Any]:
        """Move to next exercise in session"""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        if session.current_exercise_index < len(session.exercises) - 1:
            session.current_exercise_index += 1
            
        return self._get_current_exercise_state(session)
    
    def previous_exercise(self, session_id: str) -> Dict[str, Any]:
        """Move to previous exercise in session"""
        session = self.active_sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        if session.current_exercise_index > 0:
            session.current_exercise_index -= 1
            
        return self._get_current_exercise_state(session)
    
    def _get_current_exercise_state(
        self,
        session: WorkoutSession
    ) -> Dict[str, Any]:
        """Get current exercise state"""
        exercise_ids = list(session.exercises.keys())
        if not exercise_ids:
            return {}
            
        current_id = exercise_ids[session.current_exercise_index]
        exercise = session.exercises[current_id]
        
        return {
            "exercise_id": current_id,
            "sets_completed": len(exercise.sets_completed),
            "target_sets": exercise.target_sets,
            "target_reps": exercise.target_reps,
            "rest_duration": exercise.rest_duration
        }
    
    def _generate_session_summary(
        self,
        session: WorkoutSession
    ) -> Dict[str, Any]:
        """Generate summary of completed workout session"""
        total_sets = 0
        total_volume = 0
        exercise_summaries = {}
        
        for ex_id, exercise in session.exercises.items():
            sets = exercise.sets_completed
            exercise_volume = sum(s.weight * s.reps for s in sets)
            
            exercise_summaries[ex_id] = {
                "sets_completed": len(sets),
                "total_reps": sum(s.reps for s in sets),
                "total_volume": exercise_volume
            }
            
            total_sets += len(sets)
            total_volume += exercise_volume
        
        duration = datetime.now() - session.start_time
        
        return {
            "session_id": session.session_id,
            "duration_minutes": duration.total_seconds() / 60,
            "total_sets": total_sets,
            "total_volume": total_volume,
            "exercises": exercise_summaries
        }
