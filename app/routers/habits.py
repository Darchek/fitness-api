from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from app.core import parse_date
from app.db.session import get_db
from app.db.models.habits import HabitLog
from app.schemas.habits import HabitOut

router = APIRouter(prefix="/habits", tags=["habits"])


@router.get("", response_model=List[HabitOut])
async def list_habits(
    from_date_str: Optional[str] = Query(None, alias="from"),
    to_date_str: Optional[str] = Query(None, alias="to"),
    habit: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):

    from_date = parse_date(from_date_str)
    to_date = parse_date(to_date_str)

    q = select(HabitLog).order_by(HabitLog.event_date.desc())
    if from_date:
        q = q.where(HabitLog.event_date >= from_date)
    if to_date:
        q = q.where(HabitLog.event_date <= to_date)
    if habit:
        q = q.where(and_(HabitLog.habit == habit))
    result = await db.execute(q)
    return result.scalars().all()
