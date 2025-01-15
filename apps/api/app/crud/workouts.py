from typing import List, Optional, Union, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import date, timedelta, datetime
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
        self, db: Session, *, user_id: UUID, skip: int = 0, limit: int = 100,
        date_range: Optional[tuple[date, date]] = None, status: Optional[str] = None
    ) -> List[WorkoutLog]:
        query = db.query(self.model).filter(self.model.user_id == user_id)
        
        if date_range:
            start_date, end_date = date_range
            query = query.filter(
                self.model.date >= start_date,
                self.model.date <= end_date
            )
        
        if status:
            query = query.filter(self.model.status == status)
        
        return query.order_by(self.model.date.desc()).offset(skip).limit(limit).all()

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

    def get_ongoing_log(self, db: Session, user_id: UUID) -> Optional[WorkoutLog]:
        """Get the user's ongoing workout log"""
        return (
            db.query(self.model)
            .filter(
                self.model.user_id == user_id,
                self.model.status == "ongoing"
            )
            .first()
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

    def create_from_template(
        self,
        db: Session,
        *,
        user_id: UUID,
        template_id: UUID
    ) -> WorkoutLog:
        """Create a new workout log from a template"""
        template = workout_templates.get(db, id=template_id)
        if not template:
            raise ValueError(f"Template {template_id} not found")

        # Initialize exercises with completed status and empty sets
        exercises = []
        for ex in template.exercises:
            exercises.append({
                **ex,
                "completed": False,
                "sets": []
            })

        log = WorkoutLog(
            user_id=user_id,
            template_id=template_id,
            exercises=exercises,
            status="ongoing",
            date=datetime.now().date(),
            start_time=datetime.now()
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def update(
        self,
        db: Session,
        *,
        db_obj: WorkoutLog,
        obj_in: Union[WorkoutLogUpdate, Dict[str, Any]]
    ) -> WorkoutLog:
        update_data = obj_in.model_dump(exclude_unset=True) if not isinstance(obj_in, dict) else obj_in
        
        # Handle exercises field separately
        if "exercises" in update_data:
            exercises_data = json.loads(
                json.dumps(update_data["exercises"], cls=UUIDEncoder)
            )
            update_data["exercises"] = exercises_data

        # Update other fields
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

workout_templates = CRUDWorkoutTemplate(WorkoutTemplate)
workout_logs = CRUDWorkoutLog(WorkoutLog) 