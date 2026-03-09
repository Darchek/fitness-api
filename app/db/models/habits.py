from sqlalchemy import Column, Integer, String, Date, Text
from app.db.base import Base


class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Integer, primary_key=True)
    event_date = Column(Date, nullable=False)
    habit = Column(String, nullable=False)
    notes = Column(Text)
