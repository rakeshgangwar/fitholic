from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.chat import ChatContext
from app.core.logging import get_logger

logger = get_logger(__name__)

class ChatContextService:
    """Service for managing chat context"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_context(
        self,
        session_id: str,
        context_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get context for a chat session"""
        try:
            query = self.db.query(ChatContext).filter(
                ChatContext.session_id == session_id
            )
            
            if context_type:
                query = query.filter(ChatContext.context_type == context_type)
            
            context = query.order_by(ChatContext.updated_at.desc()).first()
            
            return context.context_data if context else {}
        except Exception as e:
            logger.error(f"Error fetching chat context: {str(e)}")
            return {}
    
    async def update_context(
        self,
        session_id: str,
        context_type: str,
        context_data: Dict[str, Any]
    ) -> ChatContext:
        """Update or create context for a chat session"""
        try:
            # Try to find existing context
            context = (
                self.db.query(ChatContext)
                .filter(
                    ChatContext.session_id == session_id,
                    ChatContext.context_type == context_type
                )
                .first()
            )
            
            if context:
                # Update existing context
                context.context_data = context_data
            else:
                # Create new context
                context = ChatContext(
                    session_id=session_id,
                    context_type=context_type,
                    context_data=context_data
                )
                self.db.add(context)
            
            self.db.commit()
            self.db.refresh(context)
            return context
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating chat context: {str(e)}")
            raise
    
    async def clear_context(
        self,
        session_id: str,
        context_type: Optional[str] = None
    ) -> None:
        """Clear context for a chat session"""
        try:
            query = self.db.query(ChatContext).filter(
                ChatContext.session_id == session_id
            )
            
            if context_type:
                query = query.filter(ChatContext.context_type == context_type)
            
            query.delete()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error clearing chat context: {str(e)}")
            raise 