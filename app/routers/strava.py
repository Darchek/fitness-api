import math

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
from app.core import parse_date
from app.core.http_client import HttpClient
from app.db.models import BikeMetric
from app.db.session import get_db
from app.db.models.cardio import CardioWorkout
from app.schemas.bike import BikeMetricBase
from app.schemas.cardio import CardioBase

router = APIRouter(prefix="/strava", tags=["strava"])



@router.get("/activities")
async def list_activities():
    return await HttpClient.get_activities()


@router.get("/activity/{activity_id}")
async def get_activity_by_id(
    activity_id: str
):
    return await HttpClient.get_activity(activity_id)


@router.get("/activity/{activity_id}/stream", response_model=list[BikeMetricBase])
async def get_activity_stream_by_id(
    activity_id: str,
    db: AsyncSession = Depends(get_db),
):
    stream = await HttpClient.get_activity_stream(activity_id)
    strava_hrs = stream["heartrate"]["data"]

    """
        result = await db.execute(
        select(BikeMetric)
        .where(and_(BikeMetric.session_id == 108))
    )
    bike_session = result.scalars().all()
    bike_total_len = len(bike_session)
    strava_total_len = len(strava_hrs)
    
    for idx, metric in enumerate(bike_session):
        strapol = math.floor((idx / bike_total_len) * strava_total_len)
        bike_session[idx].heart_rate = strava_hrs[strapol]
    await db.commit()
    """
    return strava_hrs