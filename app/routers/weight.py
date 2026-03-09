from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import date

from app.core import parse_date
from app.db.session import get_db
from app.db.models.weight import WeightLog
from app.schemas.weight import WeightOut

router = APIRouter(prefix="/weight", tags=["weight"])


@router.get("", response_model=List[WeightOut])
async def list_weight(
    from_date_str: Optional[str] = Query(None, alias="from"),
    to_date_str: Optional[str] = Query(None, alias="to"),
    db: AsyncSession = Depends(get_db),
):
    from_date = parse_date(from_date_str)
    to_date = parse_date(to_date_str)

    q = select(WeightLog).order_by(WeightLog.measured_at.desc())
    if from_date:
        q = q.where(WeightLog.measured_at >= from_date)
    if to_date:
        q = q.where(WeightLog.measured_at <= to_date)
    result = await db.execute(q)
    return result.scalars().all()
