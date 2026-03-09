from sqlalchemy import Column, Integer, Float, DateTime, func, Text
from app.db.base import Base


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Integer, primary_key=True)
    measured_at = Column(DateTime, nullable=False)
    value = Column("weight_kg", Float, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
