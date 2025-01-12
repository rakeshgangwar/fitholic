from typing import Dict, Any, List
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.orm import Session
from app.agents.llm_config import get_llm
from app.schemas.workout import WorkoutTemplateCreate, TemplateExercise
from app.core.logging import get_logger
from app.services.exercise_service import ExerciseService
from app.services.ai.exercise_generator import generate_exercise_with_ai
from app.crud import exercises

logger = get_logger(__name__)

class WorkoutExercise(BaseModel):
    """Schema for an exercise in the workout plan"""
    name: str = Field(..., description="The name of the exercise (e.g., 'Push-ups', 'Dumbbell Squats')")
    sets: int = Field(..., description="Number of sets to perform")
    reps: int = Field(..., description="Number of repetitions per set")
    rest_time: int = Field(..., description="Rest time between sets in seconds")
    target_muscles: List[str] = Field(..., description="List of primary muscle groups targeted")
    equipment_needed: List[str] = Field(..., description="List of equipment required for the exercise")

class WorkoutPlan(BaseModel):
    """Schema for the complete workout plan"""
    name: str = Field(..., description="Name of the workout")
    description: str = Field(..., description="Description of the workout")
    difficulty: str = Field(..., description="Difficulty level: beginner, intermediate, or advanced")
    exercises: List[WorkoutExercise] = Field(..., description="List of exercises in the workout")

class WorkoutGenerator:
    """Service for generating personalized workouts using LangChain"""
    
    def __init__(self, db: Session):
        logger.info("Initializing WorkoutGenerator service")
        self.db = db
        self.exercise_service = ExerciseService(db)
        
        # Get the LLM optimized for workout generation
        self.llm = get_llm(workflow_type="workout_generation")
        
        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert fitness trainer specialized in creating 
            personalized workout plans. Consider the user's goals, fitness level, and preferences 
            when generating workouts. 
            
            Important: For each exercise, provide a clear, standard exercise name that would be found 
            in a typical exercise database (e.g., "Push-ups", "Dumbbell Squats", "Plank").
            Also provide the primary muscle groups targeted by each exercise.
            
            The workout plan should include:
            1. 2-3 Warm-up exercises (low intensity, 1-2 sets)
            2. 4-6 Main workout exercises with sets and reps
            3. 2-3 Cool-down/stretching exercises (low intensity, 1 set)
            4. Rest periods between exercises (in seconds)
            
            Make sure exercises match the available equipment and fitness level.
            Include a mix of exercises targeting different muscle groups.
            Use standard, well-known exercise names.
            For each exercise, specify the target muscle groups and required equipment."""),
            ("user", """
            Based on the following user profile and preferences:
            Goals: {goals}
            Fitness Level: {fitness_level}
            Available Equipment: {equipment}
            Time Available: {time_available} minutes
            
            Generate a workout plan that matches the user's profile.
            """)
        ])
        
        # Create the chain with structured output
        self.chain = self.prompt | self.llm.with_structured_output(WorkoutPlan)
    
    async def _get_or_create_exercise(
        self, 
        exercise_data: WorkoutExercise,
        difficulty: str,
        available_equipment: List[str]
    ) -> str:
        """Get exercise ID from database or create if not exists"""
        logger.debug(f"Looking up or creating exercise: {exercise_data.name}")
        
        # Try to find existing exercise
        exercise = self.exercise_service.get_exercise_by_name(exercise_data.name)
        if exercise:
            logger.debug(f"Found existing exercise: {exercise.name}")
            return str(exercise.exercise_id)
        
        # Exercise not found, create it using AI
        try:
            logger.info(f"Generating new exercise: {exercise_data.name}")
            exercise_create = await generate_exercise_with_ai(
                exercise_type=exercise_data.name,
                target_muscles=exercise_data.target_muscles,
                available_equipment=exercise_data.equipment_needed or available_equipment,
                difficulty=difficulty,
                considerations=None  # Could be added based on user profile
            )
            
            # Save the new exercise to database
            new_exercise = exercises.create(self.db, obj_in=exercise_create)
            logger.info(f"Created new exercise: {new_exercise.name}")
            return str(new_exercise.exercise_id)
            
        except Exception as e:
            logger.error(f"Failed to create exercise: {str(e)}")
            raise ValueError(f"Could not create exercise '{exercise_data.name}': {str(e)}")
    
    async def generate_workout(self, user_profile: Dict[str, Any]) -> WorkoutTemplateCreate:
        """Generate a personalized workout based on user profile"""
        logger.info(f"Generating workout for user with goals: {user_profile.get('fitness_goals')}")
        try:
            # Get available exercises for the user's equipment
            available_exercises = self.exercise_service.get_exercises_by_criteria(
                equipment=user_profile.get("available_equipment"),
                difficulty=user_profile.get("fitness_level")
            )
            
            # Generate workout using the chain with structured output
            workout_plan = await self.chain.ainvoke({
                "goals": user_profile.get("fitness_goals", []),
                "fitness_level": user_profile.get("fitness_level", "beginner"),
                "equipment": user_profile.get("available_equipment", []),
                "time_available": user_profile.get("preferred_workout_duration", 60)
            })
            
            # Convert response to WorkoutTemplateCreate
            exercises_list = []
            for ex in workout_plan.exercises:
                try:
                    # Get or create the exercise
                    exercise_id = await self._get_or_create_exercise(
                        exercise_data=ex,
                        difficulty=workout_plan.difficulty,
                        available_equipment=user_profile.get("available_equipment", [])
                    )
                    
                    exercises_list.append(
                        TemplateExercise(
                            exercise_id=exercise_id,
                            sets=ex.sets,
                            reps=ex.reps,
                            rest_time=ex.rest_time
                        )
                    )
                except ValueError as e:
                    logger.warning(f"Skipping exercise: {str(e)}")
                    continue
            
            if not exercises_list:
                logger.error("No valid exercises could be created from the generated workout")
                raise ValueError("No valid exercises could be created from the generated workout")
            
            workout_template = WorkoutTemplateCreate(
                name=workout_plan.name,
                description=workout_plan.description,
                difficulty=workout_plan.difficulty,
                exercises=exercises_list
            )
            
            logger.info("Successfully generated workout template")
            return workout_template
            
        except Exception as e:
            logger.error(f"Error generating workout: {str(e)}", exc_info=True)
            raise Exception(f"Workout generation failed: {str(e)}") 