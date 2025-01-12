from typing import Dict, Any
from pydantic import BaseModel
from app.core.config import settings

class AgentConfig(BaseModel):
    """Base configuration for agents"""
    model_name: str = "gpt-4o"
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.95
    
    class Config:
        arbitrary_types_allowed = True

class WorkoutAgentConfig(AgentConfig):
    """Configuration for workout generation agent"""
    system_prompt: str = """You are an expert fitness trainer specialized in creating 
    personalized workout plans. Consider the user's goals, fitness level, and preferences 
    when generating workouts."""

class FormAnalysisConfig(AgentConfig):
    """Configuration for form analysis agent"""
    system_prompt: str = """You are an expert in exercise form and biomechanics. 
    Analyze exercise form and provide detailed, actionable feedback for improvement."""

class MotivationAgentConfig(AgentConfig):
    """Configuration for motivation agent"""
    system_prompt: str = """You are an encouraging fitness coach focused on keeping users 
    motivated and consistent with their fitness journey."""

# Agent configurations
AGENT_CONFIGS: Dict[str, Any] = {
    "workout": WorkoutAgentConfig(),
    "form": FormAnalysisConfig(),
    "motivation": MotivationAgentConfig()
} 