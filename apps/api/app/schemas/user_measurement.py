from pydantic import BaseModel, UUID4
from typing import Optional, Dict
from datetime import date, datetime

class Measurements(BaseModel):
    chest: Optional[float] = None
    waist: Optional[float] = None
    hips: Optional[float] = None
    biceps: Optional[float] = None
    thighs: Optional[float] = None
    calves: Optional[float] = None

class UserMeasurementBase(BaseModel):
    date: date
    weight: Optional[float] = None
    body_fat: Optional[float] = None
    measurements: Measurements = Measurements()

class UserMeasurementCreate(UserMeasurementBase):
    pass

class UserMeasurementUpdate(UserMeasurementBase):
    date: Optional[date] = None

class UserMeasurementInDBBase(UserMeasurementBase):
    id: UUID4
    profile_id: UUID4
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserMeasurement(UserMeasurementInDBBase):
    pass

class UserMeasurementInDB(UserMeasurementInDBBase):
    pass 