from typing import Dict, Any
from app.agents.workflows.chat.fitness_chat import FitnessChatWorkflow
from app.services.chat.history import ChatHistoryService
from app.services.chat.context import ChatContextService

class ChatService:
    """High-level service for managing chat interactions"""
    
    def __init__(self):
        self.workflow = FitnessChatWorkflow()
        self.history_service = ChatHistoryService()
        self.context_service = ChatContextService()
    
    async def process_message(
        self,
        user_id: str,
        session_id: str,
        message: str
    ) -> Dict[str, Any]:
        """Process a user message and return the response"""
        # Get chat history and context
        history = await self.history_service.get_history(session_id)
        context = await self.context_service.get_context(session_id)
        
        # Process message through workflow
        result = await self.workflow.process_message(
            message,
            {
                "user_id": user_id,
                "session_id": session_id,
                "chat_history": history,
                "context": context
            }
        )
        
        # Save message and response
        await self.history_service.add_message(session_id, "user", message)
        await self.history_service.add_message(session_id, "assistant", result["response"])
        
        # Update context if needed
        if result.get("context_update"):
            await self.context_service.update_context(
                session_id,
                result["context_update"]
            )
        
        return result 