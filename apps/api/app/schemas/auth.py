from pydantic import BaseModel, EmailStr
from uuid import UUID

class Token(BaseModel):
    """Token schema."""
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """Token data schema."""
    email: str | None = None

class TokenPayload(BaseModel):
    """Token payload schema."""
    sub: EmailStr 