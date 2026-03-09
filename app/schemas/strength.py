from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date, datetime


class StrengthBase(BaseModel):
    id: int
    created_at: date
    workout_date: date

    @field_validator("created_at", "workout_date", mode="before")
    @classmethod
    def coerce_to_date(cls, v):
        if isinstance(v, datetime):
            return v.date()
        return v

    exercise: str
    sets: Optional[int] = None
    reps_per_set: Optional[int] = None
    total_reps: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_sec: Optional[int] = None
    notes: Optional[str] = None


class StrengthCreate(BaseModel):
    workout_date: date
    exercise: str
    sets: Optional[int] = None
    reps_per_set: Optional[int] = None
    weight_kg: Optional[float] = None
    duration_sec: Optional[int] = None
    notes: Optional[str] = None


class StrengthWorkoutResponse(StrengthBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
