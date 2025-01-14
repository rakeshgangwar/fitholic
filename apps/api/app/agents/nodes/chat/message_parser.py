from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.agents.nodes.base import BaseNode
from langchain_core.prompts import ChatPromptTemplate
from app.core.logging import get_logger

logger = get_logger(__name__)

class Intent(BaseModel):
    """Schema for parsed user intent"""
    type: str = Field(..., description="Type of intent (e.g., 'log_workout', 'create_exercise', 'generate_workout')")
    confidence: float = Field(
        ..., 
        description="Confidence score for the intent classification",
        ge=0.0,
        le=1.0,
        examples=[0.8, 0.95]
    )
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Extracted parameters from the message")

class MessageParserNode(BaseNode):
    """Parse user messages to identify intents and extract parameters"""
    
    def __init__(self):
        super().__init__(
            config=None,  # Use default config
            workflow_type="chat"  # Use chat-specific LLM config
        )
        
        # Define available intents
        self.available_intents = {
            "log_workout": {
                "description": "Log a completed workout session",
                "required_params": ["workout_type", "duration"],
                "optional_params": ["exercises", "intensity", "notes"]
            },
            "create_exercise": {
                "description": "Create a new exercise in the library",
                "required_params": ["exercise_type", "target_muscles"],
                "optional_params": ["equipment", "difficulty", "considerations"]
            },
            "generate_workout": {
                "description": "Generate a workout plan",
                "required_params": ["duration"],
                "optional_params": ["type", "equipment", "target_muscles", "intensity"]
            }
        }
        
        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an AI assistant specialized in understanding fitness-related queries.
            Your task is to:
            1. Identify the user's primary intent
            2. Extract relevant parameters
            3. Assign a confidence score
            
            Available intents and their parameters:
            {intent_descriptions}
            
            Format your response as a JSON object with:
            - type: The identified intent (one of: log_workout, create_exercise, generate_workout)
            - confidence: A score between 0 and 1 (e.g., 0.8 for high confidence)
            - parameters: Extracted parameters matching the intent's requirements"""),
            ("user", "{message}")
        ])
    
    def _format_intent_descriptions(self) -> str:
        """Format available intents for the prompt"""
        descriptions = []
        for intent, details in self.available_intents.items():
            required = ", ".join(details["required_params"])
            optional = ", ".join(details["optional_params"])
            descriptions.append(
                f"- {intent}: {details['description']}\n"
                f"  Required: [{required}]\n"
                f"  Optional: [{optional}]"
            )
        return "\n".join(descriptions)
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process the message to identify intent and extract parameters"""
        try:
            message = context["current_message"]
            
            # If we're gathering requirements, don't parse for new intent
            if context.get("current_state") == "gathering_requirements":
                logger.info("MessageParser - In requirements gathering state, passing through message")
                # Keep the existing intent and just update state
                context["current_state"] = "gathering_requirements"
                return context
            
            # Get chat history for context
            history = context.get("chat_history", [])
            recent_messages = [
                f"{msg['role']}: {msg['content']}"
                for msg in history[-3:]  # Use last 3 messages for context
            ]
            
            # Create the full message with context
            full_message = "\n".join([
                "Recent conversation:",
                *recent_messages,
                "\nCurrent message:",
                message
            ])
            
            # Log the prompt being sent to LLM
            logger.info(f"MessageParser - Sending prompt to LLM:\nMessage: {message}\nHistory: {recent_messages}")
            
            # Invoke LLM with the prompt
            chain = self.prompt | self.llm.with_structured_output(Intent, method="function_calling")
            
            response = await chain.ainvoke({
                "message": full_message,
                "intent_descriptions": self._format_intent_descriptions()
            })
            
            # Log the LLM response
            logger.info(f"MessageParser - LLM Response:\nIntent: {response.type}\nConfidence: {response.confidence}\nParameters: {response.parameters}")
            
            # Update context with parsed intent
            context["current_intent"] = {
                "type": response.type,
                "confidence": response.confidence,
                "parameters": response.parameters
            }
            context["current_state"] = "intent_parsed"  # Update state to indicate parsing is complete
            
            logger.info(f"MessageParser - Updated context state: {context['current_state']}")
            return context
            
        except Exception as e:
            logger.error(f"Error parsing message: {str(e)}")
            # Fallback to a default intent with low confidence
            context["current_intent"] = {
                "type": "unknown",
                "confidence": 0.0,
                "parameters": {}
            }
            context["current_state"] = "intent_parsed"  # Still update state even in error case
            return context 