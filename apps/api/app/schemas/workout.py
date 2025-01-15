from typing import List, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, Field, validator
from datetime import datetime, date

# Template Exercise Schema
class TemplateExercise(BaseModel):
    exercise_id: UUID
    sets: int
    reps: int
    rest_time: int = Field(..., description="Rest time in seconds")

# Workout Template Schemas
class WorkoutTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    difficulty: str
    exercises: List[TemplateExercise]

class WorkoutTemplateCreate(WorkoutTemplateBase):
    pass

class WorkoutTemplateUpdate(WorkoutTemplateBase):
    name: Optional[str] = None
    difficulty: Optional[str] = None
    exercises: Optional[List[TemplateExercise]] = None

class WorkoutTemplate(WorkoutTemplateBase):
    template_id: UUID
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Workout Log Exercise Set Schema
class WorkoutSetLog(BaseModel):
    reps: int = Field(ge=0, description="Number of reps performed")
    weight: float = Field(ge=0, description="Weight in kg. 0 indicates bodyweight exercise")
    completed: bool = False

    @validator('reps')
    def validate_reps(cls, v, values):
        if values.get('completed', False) and v <= 0:
            raise ValueError("Completed sets must have at least 1 rep")
        return v

# Workout Log Exercise Schema
class WorkoutExerciseLog(BaseModel):
    exercise_id: UUID
    sets: List[WorkoutSetLog]
    completed: bool = False

    @validator('completed')
    def validate_exercise_completion(cls, v, values):
        if v and any(not s.completed for s in values.get('sets', [])):
            raise ValueError("Cannot mark exercise as completed with incomplete sets")
        return v

# Workout Log Schemas
class WorkoutLogBase(BaseModel):
    template_id: Optional[UUID] = None
    date: date
    start_time: datetime
    end_time: Optional[datetime] = None
    status: Literal["ongoing", "completed"] = "ongoing"
    duration: Optional[int] = None
    notes: Optional[str] = None
    exercises: List[WorkoutExerciseLog]

    @validator('status')
    def validate_status(cls, v, values):
        if v == "completed":
            if not values.get('end_time'):
                raise ValueError("Completed workouts must have an end time")
            if any(not e.completed for e in values.get('exercises', [])):
                raise ValueError("Cannot complete workout with incomplete exercises")
        return v

class WorkoutLogCreate(WorkoutLogBase):
    pass

class WorkoutLogUpdate(BaseModel):
    end_time: Optional[datetime] = None
    status: Optional[Literal["ongoing", "completed"]] = None
    duration: Optional[int] = None
    notes: Optional[str] = None
    exercises: Optional[List[WorkoutExerciseLog]] = None

class WorkoutLog(WorkoutLogBase):
    log_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkoutGenerationParams(BaseModel):
    duration: int = Field(ge=15, le=120)
    location: Literal['anywhere', 'home', 'gym', 'outdoor']
    equipment: List[str]
    intensity: Literal['light', 'moderate', 'intense']
    focusAreas: List[str]