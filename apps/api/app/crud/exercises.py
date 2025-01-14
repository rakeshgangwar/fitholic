from typing import List, Optional, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.crud.base import CRUDBase
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate, ExerciseUpdate

class CRUDExercise(CRUDBase[Exercise, ExerciseCreate, ExerciseUpdate]):
    def search(
        self,
        db: Session,
        *,
        muscle_groups: Optional[List[str]] = None,
        equipment: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
        name: Optional[str] = None
    ) -> List[Exercise]:
        query = db.query(self.model)
        
        if muscle_groups:
            query = query.filter(self.model.muscle_groups.overlap(muscle_groups))
        
        if equipment:
            query = query.filter(self.model.equipment.overlap(equipment))
            
        if difficulty:
            query = query.filter(self.model.difficulty == difficulty)
            
        if name:
            query = query.filter(self.model.name.ilike(f"%{name}%"))
            
        return query.all()

exercises = CRUDExercise(Exercise) 