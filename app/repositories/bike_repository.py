from __future__ import annotations

from datetime import date

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db.models import CardioWorkout
from app.db.models.bike_metrics import BikeMetric


async def list_cycling_sessions(db: AsyncSession, limit: int = 200):
    query = (
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
    result = await db.execute(query)
    return result.mappings().all()


async def get_cycling_session_by_date(db: AsyncSession, workout_date: date) -> CardioWorkout | None:
    result = await db.execute(
        select(CardioWorkout)
        .options(joinedload(CardioWorkout.metrics))
        .where(
            and_(
                CardioWorkout.type == "cycling",
                func.date(CardioWorkout.workout_date) == workout_date,
            )
        )
        .order_by(CardioWorkout.workout_date.desc())
    )
    return result.scalars().unique().first()


async def get_cycling_session_by_id(db: AsyncSession, session_id: int) -> CardioWorkout | None:
    result = await db.execute(
        select(CardioWorkout)
        .options(joinedload(CardioWorkout.metrics))
        .where(and_(CardioWorkout.id == session_id, CardioWorkout.type == "cycling"))
    )
    return result.scalars().unique().first()


async def create_cycling_session(db: AsyncSession, workout: CardioWorkout) -> CardioWorkout:
    db.add(workout)
    await db.commit()
    await db.refresh(workout)
    return workout
