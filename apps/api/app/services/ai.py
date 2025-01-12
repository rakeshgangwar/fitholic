from typing import List, Optional
from langchain.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from app.core.config import settings
from app.schemas.exercise import ExerciseCreate
from fastapi import HTTPException

exercise_prompt = PromptTemplate(
    input_variables=["exercise_type", "target_muscles", "available_equipment", "difficulty", "considerations"],
    template="""
    Generate a detailed exercise description with the following parameters:
    Exercise Type: {exercise_type}
    Target Muscles: {target_muscles}
    Available Equipment: {available_equipment}
    Difficulty Level: {difficulty}
    Special Considerations: {considerations}

    Please provide:
    1. A concise but descriptive name for the exercise
    2. A brief description of the exercise
    3. A list of primary and secondary muscle groups targeted
    4. Required equipment (if any)
    5. Detailed step-by-step instructions
    6. The appropriate difficulty level

    Format the response as a structured exercise with clear sections for each component.
    Focus on proper form, safety, and effectiveness.
    """
)

async def generate_exercise_with_ai(
    exercise_type: str,
    target_muscles: List[str],
    available_equipment: Optional[List[str]] = None,
    difficulty: Optional[str] = None,
    considerations: Optional[str] = None
) -> ExerciseCreate:
    """
    Generate exercise details using Google's Generative AI.
    """
    if not settings.GOOGLE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="AI generation is not available. GOOGLE_API_KEY is not configured."
        )

    try:
        model = ChatGoogleGenerativeAI(
            model="gemini-pro",
            temperature=0.7,
            google_api_key=settings.GOOGLE_API_KEY,
            convert_system_message_to_human=True
        )

        # Format the prompt inputs
        prompt_inputs = {
            "exercise_type": exercise_type,
            "target_muscles": ", ".join(target_muscles),
            "available_equipment": ", ".join(available_equipment) if available_equipment else "None",
            "difficulty": difficulty or "intermediate",
            "considerations": considerations or "None"
        }

        # Generate the exercise description
        prompt = exercise_prompt.format(**prompt_inputs)
        response = await model.ainvoke(prompt)
        generated_text = response.content

        # Parse the generated text into structured exercise data
        lines = generated_text.split("\n")
        exercise_data = {
            "name": "",
            "description": "",
            "muscle_groups": target_muscles,
            "equipment": available_equipment or [],
            "difficulty": difficulty,
            "instructions": "",
        }

        current_section = None
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "name:" in line.lower():
                exercise_data["name"] = line.split(":", 1)[1].strip()
            elif "description:" in line.lower():
                exercise_data["description"] = line.split(":", 1)[1].strip()
            elif "instructions:" in line.lower():
                current_section = "instructions"
            elif current_section == "instructions":
                if exercise_data["instructions"]:
                    exercise_data["instructions"] += "\n"
                exercise_data["instructions"] += line

        if not exercise_data["name"]:
            raise ValueError("Failed to generate exercise name")

        return ExerciseCreate(**exercise_data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate exercise: {str(e)}"
        ) 