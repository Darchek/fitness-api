from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date, datetime


class BikeMetricBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    idx: Optional[int] = None
    speed: Optional[float] = None
    cadence: Optional[float] = None
    resistance: Optional[float] = None
    heart_rate: Optional[float] = None
    calories: Optional[int] = None