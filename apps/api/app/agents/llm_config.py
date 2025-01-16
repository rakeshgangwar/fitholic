from typing import Dict, Any, Optional, Literal
from pydantic import BaseModel
from langchain_core.language_models import BaseLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_mistralai import ChatMistralAI
from app.core.config import settings

class BaseLLMConfig(BaseModel):
    """Base configuration for LLM providers"""
    temperature: float = 0.7
    max_tokens: int = 1000
    top_p: float = 0.95

    class Config:
        arbitrary_types_allowed = True

class GeminiConfig(BaseLLMConfig):
    """Configuration for Google's Gemini Pro"""
    provider: Literal["gemini"] = "gemini"
    model_name: str = "gemini-pro"

class OpenAIConfig(BaseLLMConfig):
    """Configuration for OpenAI models"""
    provider: Literal["openai"] = "openai"
    model_name: str = "gpt-4-turbo-preview"
    
class AnthropicConfig(BaseLLMConfig):
    """Configuration for Anthropic models"""
    provider: Literal["anthropic"] = "anthropic"
    model_name: str = "claude-3-opus-20240229"

class MistralConfig(BaseLLMConfig):
    """Configuration for Google's Mistral model"""
    provider: Literal["mistral"] = "mistral"
    model_name: str = "mistral"

LLMConfig = GeminiConfig | OpenAIConfig | AnthropicConfig

class LLMFactory:
    """Factory for creating LLM instances"""
    
    @staticmethod
    def create_llm(config: LLMConfig) -> BaseLLM:
        """Create an LLM instance based on configuration"""
        if isinstance(config, GeminiConfig):
            return ChatGoogleGenerativeAI(
                model=config.model_name,
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
                top_p=config.top_p,
                api_key=settings.GEMINI_API_KEY
            )
        elif isinstance(config, OpenAIConfig):
            return ChatOpenAI(
                model=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                api_key=settings.OPENAI_API_KEY
            )
        elif isinstance(config, AnthropicConfig):
            return ChatAnthropic(
                model=config.model_name,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
                top_p=config.top_p,
                api_key=settings.ANTHROPIC_API_KEY
            )
        elif isinstance(config, MistralConfig):
            return ChatMistralAI(
                model=config.model_name,
                temperature=config.temperature,
                max_output_tokens=config.max_tokens,
                top_p=config.top_p,
                api_key=settings.MISTRAL_API_KEY
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {config.provider}")

# Workflow-specific LLM configurations
WORKFLOW_CONFIGS = {
    "workout_generation": MistralConfig(
        model_name="mistral-large-latest",
        temperature=0.7,  # Good for creative but structured output
        max_tokens=2000   # Longer context for detailed exercise details
    ),
    "form_analysis": AnthropicConfig(
        temperature=0.3,  # Lower temperature for more precise analysis
        max_tokens=1500   # Enough context for detailed form feedback
    ),
    "nutrition_planning": OpenAIConfig(
        model_name="gpt-4-turbo-preview",
        temperature=0.5,  # Balanced between creativity and precision
        max_tokens=2500   # Longer context for detailed meal plans
    ),
    "motivation": OpenAIConfig(
        model_name="gpt-4o-mini",
        temperature=0.9,  # Higher temperature for more creative motivation
        max_tokens=1000   # Shorter, punchier motivational messages
    ),
    "chat": OpenAIConfig(
        model_name="gpt-4o",
        temperature=0.7,  # Balanced temperature for general chat
        max_tokens=1000   # Standard message length
    ),
    "exercise_generation": MistralConfig(
        model_name="mistral-large-latest",
        temperature=0.7,  # Good for creative but structured output
        max_tokens=2000   # Longer context for detailed exercise details
    )
}

def get_llm(workflow_type: Optional[str] = None, config: Optional[LLMConfig] = None) -> BaseLLM:
    """Get an LLM instance optimized for a specific workflow or using custom config"""
    if config:
        return LLMFactory.create_llm(config)
    elif workflow_type and workflow_type in WORKFLOW_CONFIGS:
        return LLMFactory.create_llm(WORKFLOW_CONFIGS[workflow_type])
    else:
        # Default to Gemini if no specific config is provided
        return LLMFactory.create_llm(GeminiConfig()) 