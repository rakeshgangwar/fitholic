from typing import Any, Dict
from langchain_core.prompts import ChatPromptTemplate
from app.agents.nodes.base import BaseNode
from app.agents.config import WorkoutAgentConfig
from app.schemas.workout import WorkoutTemplate
from app.schemas.exercise import Exercise

class WorkoutGeneratorNode(BaseNode):
    """Node for generating personalized workouts"""
    
    def __init__(self):
        super().__init__(
            config=WorkoutAgentConfig(),
            workflow_type="workout_generation"  # Use workout-specific LLM config
        )
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.config.system_prompt),
            ("user", """
            Based on the following user profile and preferences:
            Goals: {goals}
            Fitness Level: {fitness_level}
            Available Equipment: {equipment}
            Time Available: {time_available} minutes
            
            Generate a workout plan that includes:
            1. Warm-up exercises
            2. Main workout exercises with sets and reps
            3. Cool-down exercises
            4. Rest periods between exercises
            
            Format the response as a structured workout template.
            """)
        ])
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a personalized workout based on user context"""
        # Extract relevant information from context
        user_profile = context.get("user_profile", {})
        
        # Generate workout using LLM
        response = await self.llm.ainvoke(
            self.prompt.format(
                goals=user_profile.get("fitness_goals", []),
                fitness_level=user_profile.get("fitness_level", "beginner"),
                equipment=user_profile.get("available_equipment", []),
                time_available=user_profile.get("preferred_workout_duration", 60)
            )
        )
        
        # Parse LLM response into workout template
        # Note: This is a simplified version, you'll need to implement proper parsing
        workout_template = WorkoutTemplate(
            name="Generated Workout",
            description=response.content,
            difficulty=user_profile.get("fitness_level", "beginner"),
            exercises=[]  # Parse exercises from response
        )
        
        # Update context with generated workout
        context["generated_workout"] = workout_template
        return context 