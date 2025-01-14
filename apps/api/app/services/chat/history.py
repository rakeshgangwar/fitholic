from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.chat import ChatSession, ChatMessage
from app.core.logging import get_logger

logger = get_logger(__name__)

class ChatHistoryService:
    """Service for managing chat history"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_history(
        self,
        session_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent chat history for a session"""
        try:
            messages = (
                self.db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at.desc())
                .limit(limit)
                .all()
            )
            
            return [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "metadata": msg.metadata,
                    "created_at": msg.created_at.isoformat()
                }
                for msg in reversed(messages)  # Reverse to get chronological order
            ]
        except Exception as e:
            logger.error(f"Error fetching chat history: {str(e)}")
            return []
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ChatMessage:
        """Add a new message to the chat history"""
        try:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content,
                metadata=metadata
            )
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            return message
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding chat message: {str(e)}")
            raise
    
    async def create_session(self, user_id: str) -> ChatSession:
        """Create a new chat session"""
        try:
            session = ChatSession(user_id=user_id)
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)
            return session
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating chat session: {str(e)}")
            raise
    
    async def get_active_session(self, user_id: str) -> Optional[ChatSession]:
        """Get user's active chat session or create new one"""
        try:
            session = (
                self.db.query(ChatSession)
                .filter(
                    ChatSession.user_id == user_id,
                    ChatSession.status == "active"
                )
                .first()
            )
            
            if not session:
                session = await self.create_session(user_id)
            
            return session
        except Exception as e:
            logger.error(f"Error getting active session: {str(e)}")
            return None 