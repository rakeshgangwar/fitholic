from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app import crud, models, schemas
from app.core import deps
from app.core.deps import get_current_user, get_current_active_superuser

router = APIRouter()

@router.get("/me", response_model=schemas.UserProfile)
async def get_my_profile(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """Get current user's profile"""
    profile = crud.user_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.post("/me", response_model=schemas.UserProfile)
async def create_my_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: schemas.UserProfileCreate,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """Create current user's profile"""
    profile = crud.user_profile.get_by_user_id(db, user_id=current_user.id)
    if profile:
        raise HTTPException(
            status_code=400,
            detail="User already has a profile"
        )
    return crud.user_profile.create(db, obj_in=profile_in, user_id=current_user.id)

@router.put("/me", response_model=schemas.UserProfile)
async def update_my_profile(
    *,
    db: Session = Depends(deps.get_db),
    profile_in: schemas.UserProfileUpdate,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """Update current user's profile"""
    profile = crud.user_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return crud.user_profile.update(db, db_obj=profile, obj_in=profile_in)

@router.delete("/me", response_model=schemas.UserProfile)
async def delete_my_profile(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """Delete current user's profile"""
    profile = crud.user_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return crud.user_profile.remove(db, id=profile.id)

# Admin routes for managing any user's profile
@router.get("/{user_id}", response_model=schemas.UserProfile)
async def get_user_profile(
    user_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_active_superuser)
) -> Any:
    """Get any user's profile (admin only)"""
    profile = crud.user_profile.get_by_user_id(db, user_id=user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile 