from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools import YouTubeSearchTool
from app.core.config import settings
from app.schemas.exercise import ExerciseCreate
from fastapi import HTTPException
from app.core.logging import get_logger

logger = get_logger(__name__)

class ExerciseDetails(BaseModel):
    """Schema for generated exercise details"""
    name: str = Field(..., description="A concise but descriptive name for the exercise")
    description: str = Field(..., description="A brief description of what the exercise entails")
    muscle_groups: List[str] = Field(..., description="List of primary and secondary muscle groups targeted")
    equipment: List[str] = Field(..., description="List of required equipment (if any)")
    difficulty: str = Field(..., description="The appropriate difficulty level (beginner, intermediate, advanced)")
    instructions: str = Field(..., description="Detailed step-by-step instructions for performing the exercise in markdown format")
    video_url: Optional[str] = Field(None, description="URL of a YouTube video demonstrating the exercise")

# Define the prompt template using ChatPromptTemplate for better structure
exercise_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert fitness trainer specialized in creating detailed exercise descriptions.
    Focus on proper form, safety, and effectiveness when describing exercises."""),
    ("user", """Generate a detailed exercise description with the following parameters:
    Exercise Type: {exercise_type}
    Target Muscles: {target_muscles}
    Available Equipment: {available_equipment}
    Difficulty Level: {difficulty}
    Special Considerations: {considerations}
    
    Provide a complete exercise description that includes all necessary details for proper execution.""")
])


async def find_exercise_video(exercise_name: str, target_muscles: List[str]) -> Optional[str]:
    """
    Search for a relevant exercise demonstration video on YouTube.
    Returns the first regular YouTube video URL found, or None if no regular videos are found.
    """
    try:
        youtube_tool = YouTubeSearchTool()
        search_query = f"how to do {exercise_name} exercise {' '.join(target_muscles)} proper form"
        results = youtube_tool.run(search_query)
        
        try:
            import ast
            urls = ast.literal_eval(results)
            if isinstance(urls, list):
                # Find first regular YouTube URL (not shorts)
                for url in urls:
                    if 'youtube.com/watch?v=' in url:
                        video_id = url.split('watch?v=')[1].split('&')[0]
                        return f'https://youtube.com/watch?v={video_id}'
        except (ValueError, SyntaxError):
            logger.warning("Could not parse results as list, skipping")
            
        return None
    except Exception as e:
        logger.error(f"Failed to fetch YouTube video: {str(e)}")
        return None

async def generate_exercise_with_ai(
    exercise_type: str,
    target_muscles: List[str],
    available_equipment: Optional[List[str]] = None,
    difficulty: Optional[str] = None,
    considerations: Optional[str] = None
) -> ExerciseCreate:
    """
    Generate exercise details using Google's Generative AI with structured output.
    """
    try:
        model = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )

        # Format the prompt inputs
        prompt_inputs = {
            "exercise_type": exercise_type,
            "target_muscles": ", ".join(target_muscles),
            "available_equipment": ", ".join(available_equipment) if available_equipment else "None",
            "difficulty": difficulty or "intermediate",
            "considerations": considerations or "None"
        }

        # Create the chain with structured output
        chain = exercise_prompt | model.with_structured_output(ExerciseDetails)

        # Generate the exercise details
        exercise_details = await chain.ainvoke(prompt_inputs)

        # Search for a relevant YouTube video
        video_url = await find_exercise_video(exercise_details.name, target_muscles)
        exercise_details.video_url = video_url

        logger.info(f"Generated exercise details: {exercise_details}")

        # Convert to ExerciseCreate schema
        return ExerciseCreate(
            name=exercise_details.name,
            description=exercise_details.description,
            muscle_groups=exercise_details.muscle_groups,
            equipment=exercise_details.equipment,
            difficulty=exercise_details.difficulty,
            instructions=exercise_details.instructions,
            video_url=exercise_details.video_url
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate exercise: {str(e)}"
        ) 