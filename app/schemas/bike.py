from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime


class BikeMetricBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    idx: Optional[int] = None
    speed: Optional[float] = None
    distance: Optional[float] = None
    cadence: Optional[int] = None
    resistance: Optional[int] = None
    heart_rate: Optional[int] = None
    calories: Optional[int] = None
    measured_at: Optional[datetime] = None