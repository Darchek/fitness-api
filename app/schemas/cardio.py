from pydantic import BaseModel, field_validator, field_serializer
from typing import Optional, List
from datetime import date, datetime
from app.schemas.bike import BikeMetricBase


class CardioBase(BaseModel):
    id: int
    created_at: Optional[datetime] = None
    workout_date: Optional[datetime] = None
    type: str
    distance_km: Optional[float] = None
    duration_min: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    calories: Optional[int] = None
    notes: Optional[str] = None

class BikeSessionListOut(CardioBase):
    max_speed: Optional[float] = None
    avg_cadence: Optional[float] = None
    max_cadence: Optional[float] = None
    avg_resistance: Optional[float] = None
    avg_heart_rate: Optional[float] = None
    max_heart_rate: Optional[float] = None
    data_points: Optional[int] = None

    model_config = {"from_attributes": True}


class CardioCreate(BaseModel):
    type: str
    workout_date: Optional[datetime] = None
    distance_km: Optional[float] = None
    duration_min: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    calories: Optional[int] = None
    notes: Optional[str] = None


class CardioBikeSessionCreate(BaseModel):
    type: str
    workout_date: Optional[datetime] = None
    distance_km: Optional[float] = None
    duration_min: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    calories: Optional[int] = None
    notes: Optional[str] = None
    metrics: List[BikeMetricBase] = []


class CardioWorkoutResponse(CardioBase):
    id: int
    created_at: Optional[datetime] = None
    metrics: List[BikeMetricBase] = []

    model_config = {"from_attributes": True}
