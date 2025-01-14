from typing import List, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, Field
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
    reps: int
    weight: Optional[float] = None
    completed: bool = False

# Workout Log Exercise Schema
class WorkoutExerciseLog(BaseModel):
    exercise_id: UUID
    sets: List[WorkoutSetLog]

# Workout Log Schemas
class WorkoutLogBase(BaseModel):
    template_id: Optional[UUID] = None
    date: date
    duration: Optional[int] = None
    notes: Optional[str] = None
    exercises: List[WorkoutExerciseLog]

class WorkoutLogCreate(WorkoutLogBase):
    pass

class WorkoutLogUpdate(WorkoutLogBase):
    date: Optional[date] = None
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