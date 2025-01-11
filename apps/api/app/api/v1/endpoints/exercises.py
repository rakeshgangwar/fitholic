from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.exercise import (
    Exercise,
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseSearch
)
from app.crud import exercises

router = APIRouter()

@router.get("/", response_model=List[Exercise])
def list_exercises(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Exercise]:
    """
    Retrieve exercises with pagination.
    """
    return exercises.get_multi(db, skip=skip, limit=limit)

@router.post("/", response_model=Exercise, status_code=201)
def create_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_in: ExerciseCreate,
    current_user: User = Depends(get_current_user)
) -> Exercise:
    """
    Create new exercise.
    """
    return exercises.create(db, obj_in=exercise_in)

@router.get("/{exercise_id}", response_model=Exercise)
def get_exercise(
    exercise_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Exercise:
    """
    Get exercise by ID.
    """
    exercise = exercises.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found"
        )
    return exercise

@router.put("/{exercise_id}", response_model=Exercise)
def update_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_id: UUID,
    exercise_in: ExerciseUpdate,
    current_user: User = Depends(get_current_user)
) -> Exercise:
    """
    Update exercise.
    """
    exercise = exercises.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found"
        )
    exercise = exercises.update(db, db_obj=exercise, obj_in=exercise_in)
    return exercise

@router.delete("/{exercise_id}", status_code=204)
def delete_exercise(
    *,
    db: Session = Depends(get_db),
    exercise_id: UUID,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete exercise.
    """
    exercise = exercises.get(db, id=exercise_id)
    if not exercise:
        raise HTTPException(
            status_code=404,
            detail="Exercise not found"
        )
    exercises.remove(db, id=exercise_id)

@router.post("/search", response_model=List[Exercise])
def search_exercises(
    *,
    db: Session = Depends(get_db),
    search: ExerciseSearch,
    current_user: User = Depends(get_current_user)
) -> List[Exercise]:
    """
    Search exercises by various criteria.
    """
    return exercises.search(
        db,
        muscle_groups=search.muscle_groups,
        equipment=search.equipment,
        difficulty=search.difficulty,
        name=search.name
    ) 