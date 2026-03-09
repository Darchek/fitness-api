from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime
from app.schemas.bike import BikeMetricBase


class CardioBase(BaseModel):
    id: int
    created_at: date
    workout_date: date

    @field_validator("created_at", "workout_date", mode="before")
    @classmethod
    def coerce_to_date(cls, v):
        if isinstance(v, datetime):
            return v.date()
        return v


    type: str
    distance_km: Optional[float] = None
    duration_min: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    calories: Optional[int] = None
    notes: Optional[str] = None

class CardioCreate(BaseModel):
    type: str
    workout_date: date
    distance_km: Optional[float] = None
    duration_min: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    calories: Optional[int] = None
    notes: Optional[str] = None


class CardioWorkoutResponse(CardioBase):
    id: int
    created_at: Optional[datetime] = None
    metrics: List[BikeMetricBase] = []

    model_config = {"from_attributes": True}
