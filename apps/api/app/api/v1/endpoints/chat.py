from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core import deps
from app.services.chat.history import ChatHistoryService
from app.services.chat.context import ChatContextService
from app.agents.workflows.chat.fitness_chat import FitnessChatWorkflow
from app.schemas.chat import (
    ChatMessage,
    ChatResponse,
    ChatSession,
    ChatMessageCreate
)
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/sessions", response_model=ChatSession)
async def create_chat_session(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """Create a new chat session"""
    try:
        history_service = ChatHistoryService(db)
        session = await history_service.create_session(str(current_user.id))
        return ChatSession(
            session_id=str(session.session_id),
            user_id=str(session.user_id),
            status=session.status,
            created_at=session.created_at
        )
    except Exception as e:
        logger.error(f"Error creating chat session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not create chat session"
        )

@router.get("/sessions/active", response_model=ChatSession)
async def get_active_session(
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """Get or create active chat session"""
    try:
        history_service = ChatHistoryService(db)
        session = await history_service.get_active_session(str(current_user.id))
        if not session:
            raise HTTPException(status_code=404, detail="No active session found")
        
        return ChatSession(
            session_id=str(session.session_id),
            user_id=str(session.user_id),
            status=session.status,
            created_at=session.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not get active session"
        )

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_chat_history(
    session_id: str,
    limit: Optional[int] = 10,
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """Get chat history for a session"""
    try:
        history_service = ChatHistoryService(db)
        messages = await history_service.get_history(session_id, limit)
        return [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                metadata=msg["metadata"],
                created_at=msg["created_at"]
            )
            for msg in messages
        ]
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not get chat history"
        )

@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: str,
    message: ChatMessageCreate,
    *,
    db: Session = Depends(deps.get_db),
    current_user = Depends(deps.get_current_user)
):
    """Send a message to the chat"""
    try:
        # Get services
        history_service = ChatHistoryService(db)
        context_service = ChatContextService(db)
        
        # Get chat history
        chat_history = await history_service.get_history(session_id)
        
        # Get user profile from context
        user_profile = await context_service.get_context(
            session_id,
            context_type="user_profile"
        )
        
        # Process message through workflow
        workflow = FitnessChatWorkflow(db)
        result = await workflow.process_message(
            session_id=session_id,
            user_id=str(current_user.id),
            message=message.content,
            chat_history=chat_history,
            user_profile=user_profile
        )
        
        # Save user message
        await history_service.add_message(
            session_id=session_id,
            role="user",
            content=message.content
        )
        
        # Save assistant response
        assistant_message = await history_service.add_message(
            session_id=session_id,
            role="assistant",
            content=result["response"],
            metadata={
                "state": result["current_state"],
                "created_exercise": result.get("created_exercise"),
                "generated_workout": result.get("generated_workout")
            }
        )
        
        # Return formatted response
        return ChatResponse(
            session_id=session_id,
            message=ChatMessage(
                role="assistant",
                content=result["response"],
                message_metadata={
                    "state": result["current_state"],
                    "created_exercise": result.get("created_exercise"),
                    "generated_workout": result.get("generated_workout")
                },
                created_at=assistant_message.created_at
            ),
            state=result["current_state"],
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not process message"
        ) 