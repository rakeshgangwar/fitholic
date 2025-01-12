from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import date, timedelta
import json

from app.crud.base import CRUDBase
from app.models.workout import WorkoutTemplate, WorkoutLog
from app.schemas.workout import WorkoutTemplateCreate, WorkoutTemplateUpdate, WorkoutLogCreate, WorkoutLogUpdate

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)

class CRUDWorkoutTemplate(CRUDBase[WorkoutTemplate, WorkoutTemplateCreate, WorkoutTemplateUpdate]):
    def get_by_user(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[WorkoutTemplate]:
        return (
            db.query(self.model)
            .filter(self.model.created_by == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_with_user(
        self, db: Session, *, obj_in: WorkoutTemplateCreate, user_id: UUID
    ) -> WorkoutTemplate:
        obj_data = obj_in.model_dump()
        # Convert exercises list to JSON with UUID handling
        exercises_data = json.loads(
            json.dumps(obj_data["exercises"], cls=UUIDEncoder)
        )
        db_obj = WorkoutTemplate(
            **{k: v for k, v in obj_data.items() if k != "exercises"},
            exercises=exercises_data,
            created_by=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class CRUDWorkoutLog(CRUDBase[WorkoutLog, WorkoutLogCreate, WorkoutLogUpdate]):
    def get_by_user(
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[WorkoutLog]:
        return (
            db.query(self.model)
            .filter(self.model.user_id == user_id)
            .order_by(self.model.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_user_logs_by_date_range(
        self, db: Session, *, user_id: UUID, start_date: date, end_date: date
    ) -> List[WorkoutLog]:
        return (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.date >= start_date,
                self.model.date <= end_date
            )
            .order_by(self.model.date.desc())
            .all()
        )

    def create_with_user(
        self, db: Session, *, obj_in: WorkoutLogCreate, user_id: UUID
    ) -> WorkoutLog:
        obj_data = obj_in.model_dump()
        # Convert exercises list to JSON with UUID handling
        exercises_data = json.loads(
            json.dumps(obj_data["exercises"], cls=UUIDEncoder)
        )
        db_obj = WorkoutLog(
            **{k: v for k, v in obj_data.items() if k != "exercises"},
            exercises=exercises_data,
            user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

workout_templates = CRUDWorkoutTemplate(WorkoutTemplate)
workout_logs = CRUDWorkoutLog(WorkoutLog) 