from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import date, datetime

class NotificationSettings(BaseModel):
    workout_reminders: bool = True
    progress_updates: bool = True
    achievement_alerts: bool = True

class PrivacySettings(BaseModel):
    profile_visibility: str = "private"  # public, private, friends
    share_workouts: bool = False
    share_progress: bool = False

class UserProfileBase(BaseModel):
    height: Optional[float] = None  # in cm
    weight: Optional[float] = None  # in kg
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    fitness_goals: Optional[List[str]] = None
    preferred_workout_duration: Optional[int] = None  # in minutes
    preferred_workout_days: Optional[List[str]] = None
    available_equipment: Optional[List[str]] = None
    theme: Optional[str] = "system"  # light, dark, system
    language: Optional[str] = "en"
    units: Optional[str] = "metric"  # metric, imperial
    notification_settings: NotificationSettings = NotificationSettings()
    privacy_settings: PrivacySettings = PrivacySettings()

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileInDBBase(UserProfileBase):
    id: UUID4
    user_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserProfile(UserProfileInDBBase):
    pass

class UserProfileInDB(UserProfileInDBBase):
    pass 