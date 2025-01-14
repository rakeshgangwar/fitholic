from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud import exercises
from app.schemas.exercise import Exercise
from app.core.logging import get_logger

logger = get_logger(__name__)

class ExerciseService:
    """Service for managing exercises"""
    
    def __init__(self, db: Session):
        self.db = db
        logger.info("Initialized ExerciseService")
    
    def get_exercises_by_criteria(
        self,
        equipment: Optional[List[str]] = None,
        muscle_groups: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
        limit: int = 100
    ) -> List[Exercise]:
        """
        Get exercises matching the given criteria
        """
        logger.debug(f"Fetching exercises with equipment: {equipment}, muscles: {muscle_groups}, difficulty: {difficulty}")
        
        # Get all exercises first
        all_exercises = exercises.get_multi(self.db, limit=limit)
        
        # Filter exercises based on criteria
        filtered_exercises = []
        for exercise in all_exercises:
            matches = True
            
            # Check equipment
            if equipment and not any(eq in exercise.equipment for eq in equipment):
                matches = False
            
            # Check muscle groups
            if muscle_groups and not any(mg in exercise.muscle_groups for mg in muscle_groups):
                matches = False
            
            # Check difficulty
            if difficulty and exercise.difficulty != difficulty:
                matches = False
            
            if matches:
                filtered_exercises.append(exercise)
        
        logger.info(f"Found {len(filtered_exercises)} matching exercises")
        return filtered_exercises
    
    def get_exercise_by_name(self, name: str) -> Optional[Exercise]:
        """
        Get exercise by name (case-insensitive partial match)
        """
        logger.debug(f"Looking up exercise by name: {name}")
        # Get all exercises and find the best match
        # TODO: Replace with proper database query
        all_exercises = exercises.get_multi(self.db)
        
        for exercise in all_exercises:
            if name.lower() in exercise.name.lower():
                logger.debug(f"Found matching exercise: {exercise.name}")
                return exercise
        
        logger.warning(f"No matching exercise found for name: {name}")
        return None 