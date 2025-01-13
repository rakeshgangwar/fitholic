from typing import Dict, Any
from app.agents.nodes.base import BaseNode
from langchain_core.prompts import ChatPromptTemplate
from app.core.logging import get_logger

logger = get_logger(__name__)

class MotivationNode(BaseNode):
    """Node for handling general chitchat and providing motivational guidance"""
    
    def __init__(self):
        super().__init__(
            config=None,
            workflow_type="chat"
        )
        
        # Create the prompt template for general responses
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an enthusiastic and knowledgeable fitness assistant.
            Your role is to:
            1. Be encouraging and motivational
            2. Provide clear guidance about available features
            3. Help users understand how you can assist them
            4. Keep responses concise but informative
            
            Available features you can help with:
            1. Create personalized exercises based on user preferences and goals
            2. Generate workout plans that fit user's schedule and equipment
            3. Log and track workout sessions (coming soon)
            
            Current conversation context:
            {chat_history}
            
            Current user message:
            {message}
            
            Respond in a friendly, motivational tone. If the user seems interested in a specific feature,
            encourage them to try it by providing a clear example of how to use it."""),
            ("user", "{message}")
        ])
    
    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process general messages and provide guidance"""
        try:
            message = context["current_message"]
            
            # Get recent chat history for context
            history = context.get("chat_history", [])
            recent_messages = [
                f"{msg['role']}: {msg['content']}"
                for msg in history[-3:]  # Use last 3 messages for context
            ]
            
            # Format chat history
            chat_history = "\n".join(recent_messages) if recent_messages else "No previous context"
            
            # Log the prompt being sent to LLM
            logger.info(f"MotivationNode - Sending prompt to LLM:\nMessage: {message}\nHistory: {chat_history}")
            
            # Get response from LLM
            response = await self.llm.ainvoke(
                self.prompt.format(
                    message=message,
                    chat_history=chat_history
                )
            )
            
            # Log the LLM response
            logger.info(f"MotivationNode - LLM Response:\n{response.content}")
            
            # Update context with response
            context["response"] = response.content
            context["current_state"] = "motivated"  # New state for after motivation
            
            # Add suggestions for next actions
            context["response"] += "\n\nWould you like to:\n" \
                                 "1. Create a new exercise\n" \
                                 "2. Generate a workout plan\n" \
                                 "3. Learn more about other features"
            
            logger.info(f"MotivationNode - Updated context state: {context['current_state']}")
            return context
            
        except Exception as e:
            logger.error(f"Error in motivation node: {str(e)}")
            context["response"] = "I'm here to help you with your fitness journey! " \
                                "I can create exercises, generate workouts, and provide guidance. " \
                                "What would you like to try first?"
            context["current_state"] = "motivated"
            return context 