from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ChatMessageBase(BaseModel):
    """Base schema for chat messages"""
    content: str = Field(..., description="Message content")

class ChatMessageCreate(ChatMessageBase):
    """Schema for creating a chat message"""
    pass

class ChatMessage(ChatMessageBase):
    """Schema for chat message response"""
    role: str = Field(..., description="Message role (user or assistant)")
    message_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional message metadata")
    created_at: datetime = Field(..., description="Message creation timestamp")

    class Config:
        from_attributes = True

class ChatSession(BaseModel):
    """Schema for chat session"""
    session_id: str = Field(..., description="Unique session identifier")
    user_id: str = Field(..., description="User identifier")
    status: str = Field(..., description="Session status")
    created_at: datetime = Field(..., description="Session creation timestamp")

    class Config:
        from_attributes = True

class ChatResponse(BaseModel):
    """Schema for chat response"""
    session_id: str = Field(..., description="Session identifier")
    message: ChatMessage = Field(..., description="Assistant's response message")
    state: str = Field(..., description="Current conversation state")
    error: Optional[str] = Field(None, description="Error message if any")

    class Config:
        from_attributes = True

class ChatContext(BaseModel):
    """Schema for chat context"""
    context_type: str = Field(..., description="Type of context")
    context_data: Dict[str, Any] = Field(..., description="Context data")

    class Config:
        from_attributes = True 