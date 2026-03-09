from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List
from sqlalchemy.orm import joinedload
from app.schemas.cardio import CardioBase, CardioWorkoutResponse
from app.db.models import CardioWorkout
from app.db.session import get_db

router = APIRouter(prefix="/api/bike", tags=["bike"])


@router.get("", response_model=List[CardioBase])
async def list_bike_sessions(
    limit: int = Query(200),
    db: AsyncSession = Depends(get_db),
):
    q = (select(CardioWorkout).where(and_(CardioWorkout.type == "cycling"))
         .order_by(CardioWorkout.workout_date.desc()))
    q = q.limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{id}", response_model=CardioWorkoutResponse)
async def get_bike_session(_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(CardioWorkout)
        .options(joinedload(CardioWorkout.metrics))
        .where(and_(CardioWorkout.id == _id, CardioWorkout.type == "cycling"))
        .order_by(CardioWorkout.created_at)
    )
    row = result.scalars().first()
    return row
