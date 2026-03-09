from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, func
from app.db.base import Base


class StrengthWorkout(Base):
    __tablename__ = "strength_workouts"

    id = Column(Integer, primary_key=True)
    workout_date = Column(Date, nullable=False)
    exercise = Column(String, nullable=False)
    sets = Column(Integer)
    reps_per_set = Column(Integer)
    total_reps = Column(Integer)
    weight_kg = Column(Float)
    duration_sec = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
