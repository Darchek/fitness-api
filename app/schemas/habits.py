from pydantic import BaseModel
from typing import Optional
from datetime import date


class HabitOut(BaseModel):
    id: int
    event_date: date
    habit: str
    notes: Optional[str] = None

    model_config = {"from_attributes": True}
