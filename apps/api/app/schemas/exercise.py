from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    muscle_groups: List[str] = []
    equipment: List[str] = []
    difficulty: Optional[str] = None
    instructions: Optional[str] = None
    video_url: Optional[str] = None

class ExerciseCreate(ExerciseBase):
    pass

class ExerciseUpdate(ExerciseBase):
    name: Optional[str] = None

class ExerciseSearch(BaseModel):
    name: Optional[str] = None
    muscle_groups: Optional[List[str]] = None
    equipment: Optional[List[str]] = None
    difficulty: Optional[str] = None

class Exercise(ExerciseBase):
    exercise_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 