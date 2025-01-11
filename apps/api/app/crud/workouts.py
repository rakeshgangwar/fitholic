from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import date, timedelta

from app.crud.base import CRUDBase
from app.models.workout import WorkoutTemplate, WorkoutLog
from app.schemas.workout import WorkoutTemplateCreate, WorkoutTemplateUpdate, WorkoutLogCreate, WorkoutLogUpdate

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
        db_obj = WorkoutTemplate(
            **obj_in.model_dump(),
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
        db_obj = WorkoutLog(
            **obj_in.model_dump(),
            user_id=user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

workout_templates = CRUDWorkoutTemplate(WorkoutTemplate)
workout_logs = CRUDWorkoutLog(WorkoutLog) 