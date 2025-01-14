from typing import Optional, Dict, Any, Union
from uuid import UUID
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user_profile import UserProfile
from app.schemas.user_profile import UserProfileCreate, UserProfileUpdate

class CRUDUserProfile(CRUDBase[UserProfile, UserProfileCreate, UserProfileUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: UUID) -> Optional[UserProfile]:
        """Get a user's profile by user_id"""
        return db.query(self.model).filter(self.model.user_id == user_id).first()
    
    def create(self, db: Session, *, obj_in: UserProfileCreate, user_id: UUID) -> UserProfile:
        """Create a new user profile with user_id"""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data, user_id=user_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self,
        db: Session,
        *,
        db_obj: UserProfile,
        obj_in: Union[UserProfileUpdate, Dict[str, Any]]
    ) -> UserProfile:
        """Update a user profile"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        # Don't allow updating user_id
        update_data.pop("user_id", None)
        
        return super().update(db, db_obj=db_obj, obj_in=update_data)

user_profile = CRUDUserProfile(UserProfile) 