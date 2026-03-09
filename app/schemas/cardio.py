from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

from app.schemas.bike import BikeSessionOut


class CardioBase(BaseModel):
    workout_date: date
    type: str
    distance_km: Optional[float] = None
    duration_min: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    calories: Optional[int] = None
    notes: Optional[str] = None


class CardioCreate(CardioBase):
    pass


class CardioWorkoutResponse(CardioBase):
    id: int
    created_at: Optional[datetime] = None

    metrics: List[BikeSessionOut] = []

    model_config = {"from_attributes": True}
