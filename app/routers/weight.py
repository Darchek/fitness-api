import logging

from fastapi import APIRouter, Depends, Query, Body, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Any
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


"""
      {
        "kg": "{{ states('sensor.mi_body_composition_scale_26d4_mass') }}",
        "body_fat": "{{ states('sensor.xiaomi_scale_body_fat') }}"
      }
"""

@router.post("", response_model=List[WeightOut])
async def insert_weight(
    body: Any = Body(...),
    db: AsyncSession = Depends(get_db),
):
    weight_kg = body.get("kg", None)
    body_fat = body.get("body_fat", None)
    if not weight_kg or not body_fat:
        raise HTTPException(404, "No information available")

    q = select(WeightLog).order_by(WeightLog.measured_at.desc())
    result = await db.execute(q)
    item = result.scalars().first()
    if not ((item.value * 0.95) < float(weight_kg) < (item.value * 1.05)):
        logging.info(f"Discarding value of weight (kg) = {weight_kg} "
                     f"and body_fat = {body_fat}. Reference weight = {item.value}")
        raise HTTPException(402, "No expected value of weight (kg). Discarding...")

    wkg = WeightLog(value=float(weight_kg), event_name="weight_kg")
    bfat = WeightLog(value=float(body_fat), event_name="body_fat")
    db.add(wkg)
    db.add(bfat)
    await db.commit()
    logging.info(f"Added successfully weight (kg) = {weight_kg}")
    logging.info(f"Added successfully body_fat = {body_fat}")
    return [wkg, bfat]
