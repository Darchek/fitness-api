from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select
from sqlalchemy.orm import selectinload, joinedload
from typing import Optional, List
from datetime import date

from app.core.config import settings
from app.db.models import CardioWorkout
from app.db.session import get_db
from app.schemas.cardio import CardioBase

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.get("", response_model=List[CardioBase])
async def list_workouts(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
):
    effective_from = from_date or date(2026, 1, 1)
    effective_to = to_date or date.today()
    result = await db.execute(
        select(CardioWorkout)
        .where(
            CardioWorkout.created_at >= effective_from,
            CardioWorkout.created_at <= effective_to
        ).order_by(CardioWorkout.created_at)
    )
    rows = result.scalars().all()
    return rows
