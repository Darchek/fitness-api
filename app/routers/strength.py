from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date

from app.db.session import get_db
from app.db.models.strength import StrengthWorkout
from app.schemas.strength import StrengthWorkoutResponse, StrengthCreate

router = APIRouter(prefix="/api/strength", tags=["strength"])


@router.get("", response_model=List[StrengthWorkoutResponse])
async def list_strength(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    limit: int = Query(200),
    db: AsyncSession = Depends(get_db),
):
    q = select(StrengthWorkout).order_by(StrengthWorkout.workout_date.desc())
    if from_date:
        q = q.where(StrengthWorkout.workout_date >= from_date)
    if to_date:
        q = q.where(StrengthWorkout.workout_date <= to_date)
    q = q.limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=StrengthWorkoutResponse, status_code=201)
async def create_strength(payload: StrengthCreate, db: AsyncSession = Depends(get_db)):
    workout = StrengthWorkout(**payload.model_dump())
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return workout
