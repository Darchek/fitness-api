from pydantic import BaseModel
from datetime import datetime


class WeightOut(BaseModel):
    id: int
    measured_at: datetime
    value: float

    model_config = {"from_attributes": True}
