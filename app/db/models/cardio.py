from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base


class CardioWorkout(Base):
    __tablename__ = "cardio_workouts"

    id = Column(Integer, primary_key=True)
    workout_date = Column(Date, nullable=False)
    type = Column(String, nullable=False)
    distance_km = Column(Float)
    duration_min = Column(Float)
    avg_speed_kmh = Column(Float)
    calories = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    metrics = relationship("BikeMetric")


