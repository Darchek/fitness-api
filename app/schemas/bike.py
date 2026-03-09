from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class BikeMetricPoint(BaseModel):
    idx: Optional[int] = None
    speed: Optional[float] = None
    cadence: Optional[float] = None
    resistance: Optional[float] = None
    heart_rate: Optional[float] = None

    model_config = {"from_attributes": True}


class BikeSessionOut(BaseModel):
    id: int
    workout_date: date
    distance_km: Optional[float] = None
    duration_min: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    calories: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    max_speed: Optional[float] = None
    avg_cadence: Optional[float] = None
    max_cadence: Optional[float] = None
    avg_resistance: Optional[float] = None
    avg_heart_rate: Optional[float] = None
    max_heart_rate: Optional[float] = None
    data_points: Optional[int] = None

    model_config = {"from_attributes": True}


class BikeSessionDetailOut(BaseModel):
    id: int
    workout_date: date
    distance_km: Optional[float] = None
    duration_min: Optional[float] = None
    avg_speed_kmh: Optional[float] = None
    calories: Optional[int] = None
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    metrics: List[BikeMetricPoint] = []

    model_config = {"from_attributes": True}
