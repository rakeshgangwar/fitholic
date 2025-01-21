from typing import List, Optional, Literal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from datetime import date, datetime
from pydantic import BaseModel, Field

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.workout import (
    WorkoutGenerationParams,
    WorkoutTemplate,
    WorkoutTemplateCreate,
    WorkoutTemplateUpdate,
    WorkoutLog,
    WorkoutLogCreate,
    WorkoutLogUpdate
)
from app.crud import workout_templates, workout_logs, exercises
from app.services.ai.workout_generator import WorkoutGenerator

router = APIRouter()

# Workout Template endpoints
@router.get("/templates/", response_model=List[WorkoutTemplate])
def list_workout_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[WorkoutTemplate]:
    """
    Retrieve workout templates for the current user.
    """
    return workout_templates.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

@router.post("/templates/", response_model=WorkoutTemplate, status_code=201)
def create_workout_template(
    *,
    db: Session = Depends(get_db),
    template_in: WorkoutTemplateCreate,
    current_user: User = Depends(get_current_user)
) -> WorkoutTemplate:
    """
    Create new workout template.
    """
    # Validate all exercise IDs exist
    for exercise in template_in.exercises:
        if not exercises.get(db, id=exercise.exercise_id):
            raise HTTPException(
                status_code=404,
                detail=f"Exercise with ID {exercise.exercise_id} not found"
            )
    
    # Validate difficulty
    valid_difficulties = ["beginner", "intermediate", "advanced", "expert"]
    if template_in.difficulty.lower() not in valid_difficulties:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid difficulty level. Must be one of: {', '.join(valid_difficulties)}"
        )
    
    return workout_templates.create_with_user(
        db, obj_in=template_in, user_id=current_user.id
    )

@router.get("/templates/{template_id}", response_model=WorkoutTemplate)
def get_workout_template(
    template_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WorkoutTemplate:
    """
    Get specific workout template.
    """
    template = workout_templates.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Workout template not found"
        )
    if template.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    return template

@router.put("/templates/{template_id}", response_model=WorkoutTemplate)
def update_workout_template(
    *,
    db: Session = Depends(get_db),
    template_id: UUID,
    template_in: WorkoutTemplateUpdate,
    current_user: User = Depends(get_current_user)
) -> WorkoutTemplate:
    """
    Update workout template.
    """
    template = workout_templates.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Workout template not found"
        )
    if template.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    
    # Validate exercise IDs if provided
    if template_in.exercises:
        for exercise in template_in.exercises:
            if not exercises.get(db, id=exercise.exercise_id):
                raise HTTPException(
                    status_code=404,
                    detail=f"Exercise with ID {exercise.exercise_id} not found"
                )
    
    # Validate difficulty if provided
    if template_in.difficulty:
        valid_difficulties = ["beginner", "intermediate", "advanced", "expert"]
        if template_in.difficulty.lower() not in valid_difficulties:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid difficulty level. Must be one of: {', '.join(valid_difficulties)}"
            )
    
    return workout_templates.update(
        db, db_obj=template, obj_in=template_in
    )

@router.delete("/templates/{template_id}", status_code=204)
def delete_workout_template(
    *,
    db: Session = Depends(get_db),
    template_id: UUID,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete workout template.
    """
    template = workout_templates.get(db, id=template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail="Workout template not found"
        )
    if template.created_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    workout_templates.remove(db, id=template_id)

# Workout Log endpoints
@router.post("/logs", response_model=WorkoutLog)
def create_workout_log(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    workout_log: WorkoutLogCreate
) -> WorkoutLog:
    """
    Create new workout log.
    """
    # Validate template if provided
    if workout_log.template_id:
        template = workout_templates.get(db=db, id=workout_log.template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Workout template not found"
            )

    return workout_logs.create_with_user(
        db=db, 
        obj_in=workout_log, 
        user_id=current_user.id
    )

@router.put("/logs/{log_id}", response_model=WorkoutLog)
def update_workout_log(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    log_id: UUID,
    workout_log: WorkoutLogUpdate,
) -> WorkoutLog:
    """
    Update workout log.
    """
    current_log = workout_logs.get(db=db, id=log_id)
    if not current_log:
        raise HTTPException(status_code=404, detail="Workout log not found")
    if current_log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return workout_logs.update(
        db=db,
        db_obj=current_log,
        obj_in=workout_log
    )

@router.get("/logs", response_model=List[WorkoutLog])
def get_workout_logs(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
) -> List[WorkoutLog]:
    """
    Get workout logs for current user.
    """
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="Start date cannot be after end date"
        )
    
    query_filters = {}
    if start_date and end_date:
        query_filters["date_range"] = (start_date, end_date)
    if status:
        query_filters["status"] = status

    return workout_logs.get_by_user(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        **query_filters
    )

@router.get("/logs/{log_id}", response_model=WorkoutLog)
def get_workout_log(
    log_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> WorkoutLog:
    """
    Get specific workout log.
    """
    log = workout_logs.get(db, id=log_id)
    if not log:
        raise HTTPException(
            status_code=404,
            detail="Workout log not found"
        )
    if log.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    return log

@router.delete("/logs/{log_id}", status_code=204)
def delete_workout_log(
    *,
    db: Session = Depends(get_db),
    log_id: UUID,
    current_user: User = Depends(get_current_user)
) -> None:
    """
    Delete workout log.
    """
    log = workout_logs.get(db, id=log_id)
    if not log:
        raise HTTPException(
            status_code=404,
            detail="Workout log not found"
        )
    if log.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    workout_logs.remove(db, id=log_id)

@router.post("/generate", response_model=WorkoutTemplate)
async def generate_workout(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
    params: WorkoutGenerationParams
):
    """Generate a personalized workout using AI"""
    try:
        # Initialize workout generator with database session
        generator = WorkoutGenerator(db)
        
        # Prepare user profile
        user_profile = {
            "fitness_goals": current_user.profile.fitness_goals or ["general fitness"],
            "available_equipment": current_user.profile.available_equipment or [],
            "preferred_workout_duration": current_user.profile.preferred_workout_duration or 45,
            # Infer fitness level from goals and other data
            "fitness_level": "beginner"  # Default to beginner if no other info available
        }

        user_requirements = {
            "fitness_goals": params.focusAreas,
            "available_equipment": params.equipment,
            "preferred_workout_duration": params.duration,
            "location": params.location,
            "intensity": params.intensity,
            # Infer fitness level from intensity
            "fitness_level": "beginner" if params.intensity == "light" else "intermediate" if params.intensity == "moderate" else "advanced"
        }
        
        # Generate workout template
        template_in = await generator.generate_workout(user_profile, user_requirements)
        
        # Save the template
        return workout_templates.create_with_user(
            db=db,
            obj_in=template_in,
            user_id=current_user.id
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workout generation failed: {str(e)}"
        )

@router.post("/logs/{log_id}/start", response_model=WorkoutLog)
def start_workout(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    log_id: UUID,
) -> WorkoutLog:
    """
    Start a scheduled workout.
    """
    current_log = workout_logs.get(db=db, id=log_id)
    if not current_log:
        raise HTTPException(status_code=404, detail="Workout log not found")
    if current_log.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if current_log.status != "scheduled":
        raise HTTPException(status_code=400, detail="Only scheduled workouts can be started")

    return workout_logs.update(
        db=db,
        db_obj=current_log,
        obj_in={"status": "ongoing", "start_time": datetime.now()}
    ) 