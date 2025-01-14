from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.agents.nodes.base import BaseNode
from langchain_core.prompts import ChatPromptTemplate
from app.services.ai.exercise_generator import generate_exercise_with_ai
from app.core.logging import get_logger

logger = get_logger(__name__)

class ExerciseRequirements(BaseModel):
    """Schema for exercise requirements"""
    exercise_type: str = Field(..., description="Type of exercise to create")
    target_muscles: List[str] = Field(..., description="Target muscle groups")
    equipment: List[str] = Field(default_factory=list, description="Available equipment")
    difficulty: str = Field(default="intermediate", description="Desired difficulty level")
    considerations: str = Field(default=None, description="Special considerations or constraints")

class ExerciseCreatorNode(BaseNode):
    """Node for creating exercises through conversation"""
    
    def __init__(self):
        super().__init__(
            config=None,
            workflow_type="chat"
        )
        
        # Prompt for gathering missing requirements
        self.requirements_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant helping users create exercises.
            Based on the conversation, identify what information is still needed.
            
            Required information:
            - Exercise type (e.g., strength, cardio, flexibility)
            - Target muscle groups
            
            Optional information:
            - Available equipment
            - Desired difficulty level
            - Special considerations
            
            Current information: {current_info}
            
            Format your response as a question to gather the missing required information.
            If all required information is present, respond with "COMPLETE".
            """),
            ("user", "What information should I ask for next?")
        ])
    
    def _validate_requirements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and extract exercise requirements from parameters"""
        try:
            # Convert parameters to proper format
            requirements = {
                "exercise_type": params.get("exercise_type"),
                "target_muscles": params.get("target_muscles", []),
                "equipment": params.get("equipment", []),
                "difficulty": params.get("difficulty", "intermediate"),
                "considerations": params.get("considerations")
            }
            
            # Ensure target_muscles is a list
            if isinstance(requirements["target_muscles"], str):
                requirements["target_muscles"] = [requirements["target_muscles"]]
            
            # Ensure equipment is a list
            if isinstance(requirements["equipment"], str):
                requirements["equipment"] = [requirements["equipment"]]
            
            return ExerciseRequirements(**requirements).model_dump()
        except Exception as e:
            logger.error(f"Error validating requirements: {str(e)}")
            raise ValueError(f"Invalid exercise requirements: {str(e)}")
    
    async def _gather_requirements(self, context: Dict[str, Any]) -> str:
        """Gather missing requirements through conversation"""
        try:
            # Get current parameters
            params = context["current_intent"]["parameters"]
            
            # Log current parameters
            logger.info(f"ExerciseCreator - Current parameters: {params}")
            
            # Format current information
            current_info = []
            if params.get("exercise_type"):
                current_info.append(f"Exercise type: {params['exercise_type']}")
            if params.get("target_muscles"):
                current_info.append(f"Target muscles: {', '.join(params['target_muscles'])}")
            if params.get("equipment"):
                current_info.append(f"Equipment: {', '.join(params['equipment'])}")
            if params.get("difficulty"):
                current_info.append(f"Difficulty: {params['difficulty']}")
            if params.get("considerations"):
                current_info.append(f"Considerations: {params['considerations']}")
            
            current_info_str = "\n".join(current_info) if current_info else "No information provided yet"
            
            # Check if we have the required information
            has_exercise_type = bool(params.get("exercise_type"))
            has_target_muscles = bool(params.get("target_muscles"))
            
            if has_exercise_type and has_target_muscles:
                logger.info("ExerciseCreator - All required information present")
                return "COMPLETE"
            
            # Only make LLM call if we're missing required information
            logger.info("ExerciseCreator - Getting next question from LLM")
            response = await self.llm.ainvoke(
                self.requirements_prompt.format(
                    current_info=current_info_str
                )
            )
            
            logger.info(f"ExerciseCreator - LLM response: {response.content}")
            return response.content
            
        except Exception as e:
            logger.error(f"Error gathering requirements: {str(e)}")
            return "What type of exercise would you like to create?"
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the exercise creation request"""
        try:
            # Skip processing if the message is just the initial command
            if context["current_message"].strip().lower() == "create a new exercise":
                context["current_state"] = "gathering_requirements"
                context["response"] = "What type of exercise would you like to create? Please specify the type (e.g., strength, cardio, flexibility) and target muscle groups."
                logger.info("ExerciseCreator - Initial request, asking for details")
                return context

            # If we're already gathering requirements, check if the user's message provides the needed info
            if context.get("current_state") == "gathering_requirements":
                # Update parameters based on the user's response
                message = context.get("current_message", "").lower()
                current_params = context["current_intent"]["parameters"]
                
                logger.info(f"ExerciseCreator - Processing user response: {message}")
                
                # Try to extract exercise type if missing
                if not current_params.get("exercise_type"):
                    for exercise_type in ["strength", "cardio", "flexibility", "balance", "plyometric"]:
                        if exercise_type in message:
                            current_params["exercise_type"] = exercise_type
                            logger.info(f"ExerciseCreator - Extracted exercise type: {exercise_type}")
                            break
                
                # Try to extract target muscles if missing
                if not current_params.get("target_muscles"):
                    muscle_groups = ["chest", "back", "shoulders", "biceps", "triceps", "legs", "core", "full body"]
                    found_muscles = [muscle for muscle in muscle_groups if muscle in message]
                    if found_muscles:
                        current_params["target_muscles"] = found_muscles
                        logger.info(f"ExerciseCreator - Extracted target muscles: {found_muscles}")
            
            # Check if we need to gather more information
            next_question = await self._gather_requirements(context)
            
            if next_question != "COMPLETE":
                # Need more information, update context and return question
                context["current_state"] = "gathering_requirements"
                context["response"] = next_question
                logger.info(f"ExerciseCreator - Gathering requirements, next question: {next_question}")
                return context
            
            # We have all required information, validate and create exercise
            requirements = self._validate_requirements(
                context["current_intent"]["parameters"]
            )
            
            logger.info(f"ExerciseCreator - Creating exercise with requirements: {requirements}")
            
            # Generate exercise using existing service
            exercise = await generate_exercise_with_ai(
                exercise_type=requirements["exercise_type"],
                target_muscles=requirements["target_muscles"],
                available_equipment=requirements["equipment"],
                difficulty=requirements["difficulty"],
                considerations=requirements["considerations"]
            )
            
            # Update context with created exercise
            context["current_state"] = "exercise_created"
            context["created_exercise"] = exercise.model_dump()
            
            # Generate success message
            context["response"] = f"""I've created a new exercise: {exercise.name}
            
            Description: {exercise.description}
            Target Muscles: {', '.join(exercise.muscle_groups)}
            Equipment Needed: {', '.join(exercise.equipment) if exercise.equipment else 'None'}
            Difficulty: {exercise.difficulty}
            
            Would you like me to show you the detailed instructions?"""
            
            logger.info("ExerciseCreator - Exercise created successfully")
            return context
            
        except Exception as e:
            logger.error(f"Error in exercise creation: {str(e)}")
            context["current_state"] = "error"
            context["error"] = str(e)
            context["response"] = "I encountered an error while creating the exercise. Please try again with different parameters."
            return context 