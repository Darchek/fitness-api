from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from sqlalchemy.orm import joinedload
from typing import List

from app.schemas.cardio import BikeSessionListOut, CardioWorkoutResponse, CardioBikeSessionCreate
from app.db.models import CardioWorkout
from app.db.models.bike_metrics import BikeMetric
from app.db.session import get_db

router = APIRouter(prefix="/bike", tags=["bike"])


@router.get("", response_model=List[BikeSessionListOut])
async def list_bike_sessions(
    limit: int = Query(200),
    db: AsyncSession = Depends(get_db),
):
    q = (
        select(
            CardioWorkout.id,
            CardioWorkout.workout_date,
            CardioWorkout.type,
            CardioWorkout.distance_km,
            CardioWorkout.duration_min,
            CardioWorkout.avg_speed_kmh,
            CardioWorkout.calories,
            CardioWorkout.notes,
            CardioWorkout.created_at,
            func.coalesce(func.max(BikeMetric.speed), 0).label("max_speed"),
            func.coalesce(func.round(func.avg(BikeMetric.cadence), 2), 0).label("avg_cadence"),
            func.coalesce(func.max(BikeMetric.cadence), 0).label("max_cadence"),
            func.coalesce(func.round(func.avg(BikeMetric.resistance), 2), 0).label("avg_resistance"),
            func.coalesce(func.round(func.avg(BikeMetric.heart_rate), 2), 0).label("avg_heart_rate"),
            func.coalesce(func.max(BikeMetric.heart_rate), 0).label("max_heart_rate"),
            func.coalesce(func.count(BikeMetric.idx), 0).label("data_points"),
        )
        .outerjoin(BikeMetric, BikeMetric.session_id == CardioWorkout.id)
        .where(CardioWorkout.type == "cycling")
        .group_by(CardioWorkout.id)
        .order_by(CardioWorkout.workout_date.desc())
        .limit(limit)
    )
    result = await db.execute(q)
    return [BikeSessionListOut(**dict(row)) for row in result.mappings().all()]


@router.get("/{_id}", response_model=CardioWorkoutResponse)
async def get_bike_session(_id: int, db: AsyncSession = Depends(get_db)):
    return get_by_id(_id, db)

@router.post("", response_model=CardioWorkoutResponse)
async def create_bike_session(payload: CardioBikeSessionCreate, db: AsyncSession = Depends(get_db)):
    workout = CardioWorkout(
        **payload.model_dump(exclude={"metrics"}),
        metrics=[BikeMetric(**m.model_dump()) for m in payload.metrics]
    )
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return await get_by_id(workout.id, db)


async def get_by_id(_id: int, db: AsyncSession):
    result = await db.execute(
        select(CardioWorkout)
        .options(joinedload(CardioWorkout.metrics))
        .where(and_(CardioWorkout.id == _id, CardioWorkout.type == "cycling"))
        .order_by(CardioWorkout.created_at)
    )
    row = result.scalars().first()
    return row