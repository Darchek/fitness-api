from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date

from app.db.session import get_db
from app.db.models.cardio import CardioWorkout
from app.schemas.cardio import CardioBase, CardioCreate

router = APIRouter(prefix="/api/cardio", tags=["cardio"])


@router.get("", response_model=List[CardioBase])
async def list_cardio(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    exclude: Optional[str] = Query(None),
    limit: int = Query(200),
    db: AsyncSession = Depends(get_db),
):
    q = select(CardioWorkout).order_by(CardioWorkout.workout_date.desc())
    if from_date:
        q = q.where(CardioWorkout.workout_date >= from_date)
    if to_date:
        q = q.where(CardioWorkout.workout_date <= to_date)
    if exclude:
        excluded = [e.strip() for e in exclude.split(",")]
        q = q.where(CardioWorkout.type.notin_(excluded))
    q = q.limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("", response_model=CardioBase, status_code=201)
async def create_cardio(payload: CardioCreate, db: AsyncSession = Depends(get_db)):
    workout = CardioWorkout(**payload.model_dump())
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return workout
