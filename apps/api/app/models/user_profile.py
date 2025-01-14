from sqlalchemy import Column, Float, Date, String, JSON, ForeignKey, ARRAY, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    
    # Personal Info
    height = Column(Float)  # in cm
    weight = Column(Float)  # in kg
    date_of_birth = Column(Date)
    gender = Column(String)
    
    # Fitness Goals and Preferences
    fitness_goals = Column(ARRAY(String))
    preferred_workout_duration = Column(Integer)  # in minutes
    preferred_workout_days = Column(ARRAY(String))
    available_equipment = Column(ARRAY(String))
    
    # App Settings
    theme = Column(String, default="system")  # light, dark, system
    language = Column(String, default="en")
    units = Column(String, default="metric")  # metric, imperial
    
    # Notification Settings
    notification_settings = Column(JSON, default={
        "workout_reminders": True,
        "progress_updates": True,
        "achievement_alerts": True
    })
    
    # Privacy Settings
    privacy_settings = Column(JSON, default={
        "profile_visibility": "private",
        "share_workouts": False,
        "share_progress": False
    })
    
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()', onupdate='now()')
    
    # Relationships
    user = relationship("User", back_populates="profile")
    measurements = relationship("UserMeasurement", back_populates="profile", cascade="all, delete-orphan") 