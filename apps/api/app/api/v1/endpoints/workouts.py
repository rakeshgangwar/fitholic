from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.workout import (
    WorkoutTemplate,
    WorkoutTemplateCreate,
    WorkoutTemplateUpdate,
    WorkoutLog,
    WorkoutLogCreate,
    WorkoutLogUpdate
)
from app.crud import workout_templates, workout_logs, exercises
from app.agents.workflows.workout_generation import WorkoutGenerationWorkflow

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
@router.get("/logs/", response_model=List[WorkoutLog])
def list_workout_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[WorkoutLog]:
    """
    Retrieve workout logs for the current user.
    """
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="Start date cannot be after end date"
        )
    
    if start_date and end_date:
        return workout_logs.get_user_logs_by_date_range(
            db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date
        )
    return workout_logs.get_by_user(
        db, user_id=current_user.id, skip=skip, limit=limit
    )

@router.post("/logs/", response_model=WorkoutLog, status_code=201)
def create_workout_log(
    *,
    db: Session = Depends(get_db),
    log_in: WorkoutLogCreate,
    current_user: User = Depends(get_current_user)
) -> WorkoutLog:
    """
    Create new workout log.
    """
    # Validate template if provided
    if log_in.template_id:
        template = workout_templates.get(db, id=log_in.template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Workout template not found"
            )
        if template.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to use this template"
            )
    
    # Validate all exercise IDs
    for exercise in log_in.exercises:
        if not exercises.get(db, id=exercise.exercise_id):
            raise HTTPException(
                status_code=404,
                detail=f"Exercise with ID {exercise.exercise_id} not found"
            )
        
        # Validate sets data
        for set_data in exercise.sets:
            if set_data.reps < 1:
                raise HTTPException(
                    status_code=422,
                    detail="Number of reps must be greater than 0"
                )
            if set_data.weight is not None and set_data.weight <= 0:
                raise HTTPException(
                    status_code=422,
                    detail="Weight must be greater than 0"
                )
    
    return workout_logs.create_with_user(
        db, obj_in=log_in, user_id=current_user.id
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

@router.put("/logs/{log_id}", response_model=WorkoutLog)
def update_workout_log(
    *,
    db: Session = Depends(get_db),
    log_id: UUID,
    log_in: WorkoutLogUpdate,
    current_user: User = Depends(get_current_user)
) -> WorkoutLog:
    """
    Update workout log.
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
    
    # Validate template if provided
    if log_in.template_id:
        template = workout_templates.get(db, id=log_in.template_id)
        if not template:
            raise HTTPException(
                status_code=404,
                detail="Workout template not found"
            )
        if template.created_by != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions to use this template"
            )
    
    # Validate exercises if provided
    if log_in.exercises:
        for exercise in log_in.exercises:
            if not exercises.get(db, id=exercise.exercise_id):
                raise HTTPException(
                    status_code=404,
                    detail=f"Exercise with ID {exercise.exercise_id} not found"
                )
            
            # Validate sets data
            for set_data in exercise.sets:
                if set_data.reps < 1:
                    raise HTTPException(
                        status_code=422,
                        detail="Number of reps must be greater than 0"
                    )
                if set_data.weight is not None and set_data.weight <= 0:
                    raise HTTPException(
                        status_code=422,
                        detail="Weight must be greater than 0"
                    )
    
    return workout_logs.update(db, db_obj=log, obj_in=log_in)

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
    current_user = Depends(get_current_user)
):
    """Generate a personalized workout using AI"""
    try:
        # Initialize workflow
        workflow = WorkoutGenerationWorkflow()
        
        # Prepare context with user profile
        context = {
            "user_profile": {
                "fitness_goals": current_user.profile.fitness_goals,
                "fitness_level": current_user.profile.fitness_level,
                "available_equipment": current_user.profile.available_equipment,
                "preferred_workout_duration": current_user.profile.preferred_workout_duration
            }
        }
        
        # Execute workflow
        result = await workflow.execute(context)
        
        # Extract generated workout
        workout_template = result.get("generated_workout")
        if not workout_template:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate workout"
            )
        
        return workout_template
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Workout generation failed: {str(e)}"
        ) 