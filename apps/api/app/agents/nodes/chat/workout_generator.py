from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from app.agents.nodes.base import BaseNode
from langchain_core.prompts import ChatPromptTemplate
from app.services.ai.workout_generator import WorkoutGenerator
from app.core.logging import get_logger

logger = get_logger(__name__)

class WorkoutRequirements(BaseModel):
    """Schema for workout generation requirements"""
    duration: int = Field(..., description="Workout duration in minutes")
    workout_type: Optional[str] = Field(None, description="Type of workout (e.g., strength, cardio, hiit)")
    target_muscles: Optional[List[str]] = Field(None, description="Target muscle groups")
    equipment: Optional[List[str]] = Field(None, description="Available equipment")
    intensity: Optional[str] = Field("moderate", description="Desired workout intensity")

class WorkoutGeneratorNode(BaseNode):
    """Node for generating workouts through conversation"""
    
    def __init__(self, db):
        super().__init__(
            config=None,
            workflow_type="chat"
        )
        self.workout_generator = WorkoutGenerator(db)
        
        # Prompt for gathering missing requirements
        self.requirements_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant helping users create workout plans.
            Based on the conversation, identify what information is still needed.
            
            Required information:
            - Duration (in minutes)
            
            Optional information:
            - Workout type (strength, cardio, hiit, etc.)
            - Target muscle groups
            - Available equipment
            - Desired intensity
            
            Current information: {current_info}
            
            Format your response as a question to gather the missing required information.
            If all required information is present, respond with "COMPLETE".
            """),
            ("user", "What information should I ask for next?")
        ])
    
    def _validate_requirements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and extract workout requirements from parameters"""
        try:
            # Convert parameters to proper format
            requirements = {
                "duration": int(params.get("duration", 0)),
                "workout_type": params.get("type"),
                "target_muscles": params.get("target_muscles", []),
                "equipment": params.get("equipment", []),
                "intensity": params.get("intensity", "moderate")
            }
            
            # Ensure lists are properly formatted
            for field in ["target_muscles", "equipment"]:
                if isinstance(requirements[field], str):
                    requirements[field] = [requirements[field]]
            
            return WorkoutRequirements(**requirements).model_dump()
        except Exception as e:
            logger.error(f"Error validating requirements: {str(e)}")
            raise ValueError(f"Invalid workout requirements: {str(e)}")
    
    async def _gather_requirements(self, context: Dict[str, Any]) -> str:
        """Determine what information is still needed"""
        current_params = context["current_intent"]["parameters"]
        
        # Format current information for the prompt
        current_info = "\n".join([
            f"- {key}: {value}"
            for key, value in current_params.items()
            if value is not None
        ])
        
        # Ask LLM what information is still needed
        response = await self.llm.ainvoke(
            self.requirements_prompt.format(current_info=current_info)
        )
        
        return response.content
    
    def _format_workout_summary(self, workout: Dict[str, Any]) -> str:
        """Generate a user-friendly summary of the workout"""
        exercises = workout.get("exercises", [])
        
        summary = [
            f"Here's your {workout['duration']} minute {workout.get('workout_type', '')} workout:",
            "",
            f"Difficulty: {workout['difficulty']}",
            "",
            "Exercises:"
        ]
        
        for i, exercise in enumerate(exercises, 1):
            summary.append(
                f"{i}. {exercise['name']}: "
                f"{exercise['sets']} sets × {exercise['reps']} reps "
                f"(Rest: {exercise['rest_time']}s)"
            )
        
        summary.extend([
            "",
            "Would you like to:",
            "1. Start this workout",
            "2. See detailed instructions for any exercise",
            "3. Modify the workout",
            "4. Save it as a template"
        ])
        
        return "\n".join(summary)
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the workout generation request"""
        try:
            # Check if we need to gather more information
            next_question = await self._gather_requirements(context)
            
            if next_question != "COMPLETE":
                # Need more information, update context and return question
                context["current_state"] = "gathering_requirements"
                context["next_question"] = next_question
                return context
            
            # We have all required information, validate and generate workout
            requirements = self._validate_requirements(
                context["current_intent"]["parameters"]
            )
            
            # Get user profile from context
            user_profile = context.get("user_profile", {})
            
            # Update user profile with workout requirements
            user_profile.update({
                "preferred_workout_duration": requirements["duration"],
                "available_equipment": requirements["equipment"],
                "fitness_goals": [requirements["workout_type"]] if requirements["workout_type"] else []
            })
            
            # Generate workout using existing service
            workout = await self.workout_generator.generate_workout(user_profile)
            
            # Update context with generated workout
            context["current_state"] = "workout_generated"
            context["generated_workout"] = workout.model_dump()
            
            # Generate success message with workout summary
            context["response"] = self._format_workout_summary(workout.model_dump())
            
            return context
            
        except Exception as e:
            logger.error(f"Error in workout generation: {str(e)}")
            context["current_state"] = "error"
            context["error"] = str(e)
            context["response"] = "I encountered an error while generating the workout. Please try again with different parameters."
            return context 