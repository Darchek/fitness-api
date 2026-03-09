from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func
from app.db.base import Base


class BikeMetric(Base):
    __tablename__ = "bike_metrics"

    session_id = Column(Integer, ForeignKey("cardio_workouts.id"), primary_key=True)
    idx = Column(Integer, primary_key=True)
    speed = Column(Float)
    cadence = Column(Float)
    resistance = Column(Float)
    heart_rate = Column(Float)
    measured_at = Column(DateTime, server_default=func.now())
