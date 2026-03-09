from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, func
from app.db.base import Base


class BikeMetric(Base):
    __tablename__ = "bike_metrics"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("cardio_workouts.id"), nullable=False)
    idx = Column(Integer)
    speed = Column(Float)
    cadence = Column(Float)
    resistance = Column(Float)
    heart_rate = Column(Float)
    created_at = Column(DateTime, server_default=func.now())
