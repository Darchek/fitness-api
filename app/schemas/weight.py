from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class WeightOut(BaseModel):
    id: int
    measured_at: datetime
    value: float
    event_name: str
    notes: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
