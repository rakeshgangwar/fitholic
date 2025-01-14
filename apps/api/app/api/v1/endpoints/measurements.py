from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date

from app import crud, models, schemas
from app.core import deps
from app.core.deps import get_current_user

router = APIRouter()

@router.get("/me", response_model=List[schemas.UserMeasurement])
async def get_my_measurements(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user),
    skip: int = 0,
    limit: int = Query(default=100, lte=100)
) -> Any:
    """Get current user's measurements"""
    profile = crud.user_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return crud.user_measurement.get_by_profile(
        db, profile_id=profile.id, skip=skip, limit=limit
    )

@router.post("/me", response_model=schemas.UserMeasurement)
async def create_my_measurement(
    *,
    db: Session = Depends(deps.get_db),
    measurement_in: schemas.UserMeasurementCreate,
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """Create a new measurement for current user"""
    profile = crud.user_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    # Check if measurement for this date already exists
    existing = crud.user_measurement.get_by_date(
        db, profile_id=profile.id, measurement_date=measurement_in.date
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Measurement for this date already exists"
        )
    
    return crud.user_measurement.create(db, obj_in=measurement_in, profile_id=profile.id)

@router.get("/me/{measurement_id}", response_model=schemas.UserMeasurement)
async def get_my_measurement(
    measurement_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """Get a specific measurement for current user"""
    profile = crud.user_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    measurement = crud.user_measurement.get(db, id=measurement_id)
    if not measurement or measurement.profile_id != profile.id:
        raise HTTPException(status_code=404, detail="Measurement not found")
    return measurement

@router.put("/me/{measurement_id}", response_model=schemas.UserMeasurement)
async def update_my_measurement(
    *,
    measurement_id: UUID,
    measurement_in: schemas.UserMeasurementUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """Update a measurement for current user"""
    profile = crud.user_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    measurement = crud.user_measurement.get(db, id=measurement_id)
    if not measurement or measurement.profile_id != profile.id:
        raise HTTPException(status_code=404, detail="Measurement not found")
    
    return crud.user_measurement.update(db, db_obj=measurement, obj_in=measurement_in)

@router.delete("/me/{measurement_id}", response_model=schemas.UserMeasurement)
async def delete_my_measurement(
    measurement_id: UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(get_current_user)
) -> Any:
    """Delete a measurement for current user"""
    profile = crud.user_profile.get_by_user_id(db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    measurement = crud.user_measurement.get(db, id=measurement_id)
    if not measurement or measurement.profile_id != profile.id:
        raise HTTPException(status_code=404, detail="Measurement not found")
    
    return crud.user_measurement.remove(db, id=measurement_id) 