from sqlalchemy import Column, Integer, Float, DateTime, func
from app.db.base import Base


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True)
    measured_at = Column(DateTime, nullable=False)
    value = Column(Float, nullable=False)
