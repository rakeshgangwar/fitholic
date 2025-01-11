from typing import List
from sqlalchemy import Column, String, ARRAY, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base

class Exercise(Base):
    __tablename__ = "exercises"

    exercise_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    muscle_groups = Column(ARRAY(String), nullable=False, default=[])
    equipment = Column(ARRAY(String), nullable=False, default=[])
    difficulty = Column(String, nullable=True)
    instructions = Column(String, nullable=True)
    video_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 