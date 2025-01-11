from typing import List
from sqlalchemy import Column, String, ARRAY, DateTime, ForeignKey, Integer, Boolean, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class WorkoutTemplate(Base):
    __tablename__ = "workout_templates"

    template_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    difficulty = Column(String, nullable=False)
    exercises = Column(JSON, nullable=False)  # Will store array of {exerciseId, sets, reps, restTime}
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()', onupdate='now()')

    # Relationships
    user = relationship("User", back_populates="workout_templates")
    workout_logs = relationship("WorkoutLog", back_populates="template")

class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("workout_templates.template_id"), nullable=True)
    date = Column(Date, nullable=False)
    duration = Column(Integer, nullable=True)  # in minutes
    notes = Column(String, nullable=True)
    exercises = Column(JSON, nullable=False)  # Will store array of {exerciseId, sets: [{reps, weight, completed}]}
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()', onupdate='now()')

    # Relationships
    user = relationship("User", back_populates="workout_logs")
    template = relationship("WorkoutTemplate", back_populates="workout_logs") 