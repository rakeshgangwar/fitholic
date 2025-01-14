from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from sqlalchemy.orm import Session
from datetime import date

from app.crud.base import CRUDBase
from app.models.user_measurement import UserMeasurement
from app.schemas.user_measurement import UserMeasurementCreate, UserMeasurementUpdate

class CRUDUserMeasurement(CRUDBase[UserMeasurement, UserMeasurementCreate, UserMeasurementUpdate]):
    def get_by_profile(
        self, db: Session, *, profile_id: UUID, skip: int = 0, limit: int = 100
    ) -> List[UserMeasurement]:
        """Get all measurements for a profile"""
        return (
            db.query(self.model)
            .filter(self.model.profile_id == profile_id)
            .order_by(self.model.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_date(
        self, db: Session, *, profile_id: UUID, measurement_date: date
    ) -> Optional[UserMeasurement]:
        """Get a measurement for a specific date"""
        return (
            db.query(self.model)
            .filter(
                self.model.profile_id == profile_id,
                self.model.date == measurement_date
            )
            .first()
        )
    
    def create(
        self, db: Session, *, obj_in: UserMeasurementCreate, profile_id: UUID
    ) -> UserMeasurement:
        """Create a new measurement with profile_id"""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data, profile_id=profile_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: UserMeasurement,
        obj_in: Union[UserMeasurementUpdate, Dict[str, Any]]
    ) -> UserMeasurement:
        """Update a user measurement"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Don't allow updating profile_id
        update_data.pop("profile_id", None)
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

user_measurement = CRUDUserMeasurement(UserMeasurement) 