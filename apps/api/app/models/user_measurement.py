from sqlalchemy import Column, Float, Date, ForeignKey, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base

class UserMeasurement(Base):
    __tablename__ = "user_measurements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"), nullable=False)
    date = Column(Date, nullable=False)
    
    # Core measurements
    weight = Column(Float)  # in kg
    body_fat = Column(Float)  # percentage
    
    # Additional measurements in cm
    measurements = Column(JSON, default={
        "chest": None,
        "waist": None,
        "hips": None,
        "biceps": None,
        "thighs": None,
        "calves": None
    })
    
    created_at = Column(DateTime(timezone=True), server_default='now()')
    updated_at = Column(DateTime(timezone=True), server_default='now()', onupdate='now()')
    
    # Relationships
    profile = relationship("UserProfile", back_populates="measurements") 