from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class StrengthBase(BaseModel):
    workout_date: date
    exercise: str
    sets: Optional[int] = None
    reps_per_set: Optional[int] = None
    total_reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_sec: Optional[int] = None
    notes: Optional[str] = None


class StrengthCreate(StrengthBase):
    pass


class StrengthOut(StrengthBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
