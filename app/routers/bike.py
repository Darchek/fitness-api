from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List

from app.db.session import get_db
from app.schemas.bike import BikeSessionOut, BikeSessionDetailOut, BikeMetricPoint

router = APIRouter(prefix="/api/bike", tags=["bike"])


@router.get("", response_model=List[BikeSessionOut])
async def list_bike_sessions(
    limit: int = Query(200),
    db: AsyncSession = Depends(get_db),
):
    sql = text("""
        SELECT
            c.id, c.workout_date, c.distance_km, c.duration_min,
            c.avg_speed_kmh, c.calories, c.notes, c.created_at,
            MAX(b.speed) AS max_speed,
            AVG(b.cadence) AS avg_cadence,
            MAX(b.cadence) AS max_cadence,
            AVG(b.resistance) AS avg_resistance,
            AVG(b.heart_rate) AS avg_heart_rate,
            MAX(b.heart_rate) AS max_heart_rate,
            COUNT(b.id) AS data_points
        FROM cardio_workouts c
        LEFT JOIN bike_metrics b ON b.session_id = c.id
        WHERE c.type = 'cycling'
        GROUP BY c.id
        ORDER BY c.workout_date DESC
        LIMIT :limit
    """)
    result = await db.execute(sql, {"limit": limit})
    rows = result.mappings().all()
    return [
        BikeSessionOut(
            id=r["id"],
            workout_date=r["workout_date"],
            distance_km=float(r["distance_km"]) if r["distance_km"] is not None else None,
            duration_min=float(r["duration_min"]) if r["duration_min"] is not None else None,
            avg_speed_kmh=float(r["avg_speed_kmh"]) if r["avg_speed_kmh"] is not None else None,
            calories=r["calories"],
            notes=r["notes"],
            created_at=r["created_at"],
            max_speed=float(r["max_speed"]) if r["max_speed"] is not None else None,
            avg_cadence=float(r["avg_cadence"]) if r["avg_cadence"] is not None else None,
            max_cadence=float(r["max_cadence"]) if r["max_cadence"] is not None else None,
            avg_resistance=float(r["avg_resistance"]) if r["avg_resistance"] is not None else None,
            avg_heart_rate=float(r["avg_heart_rate"]) if r["avg_heart_rate"] is not None else None,
            max_heart_rate=float(r["max_heart_rate"]) if r["max_heart_rate"] is not None else None,
            data_points=r["data_points"],
        )
        for r in rows
    ]


@router.get("/{session_id}", response_model=BikeSessionDetailOut)
async def get_bike_session(session_id: int, db: AsyncSession = Depends(get_db)):
    session_sql = text("""
        SELECT id, workout_date, distance_km, duration_min, avg_speed_kmh, calories, notes, created_at
        FROM cardio_workouts
        WHERE id = :id AND type = 'cycling'
    """)
    session_result = await db.execute(session_sql, {"id": session_id})
    session = session_result.mappings().first()
    if not session:
        raise HTTPException(status_code=404, detail="Bike session not found")

    metrics_sql = text("""
        SELECT idx, speed, cadence, resistance, heart_rate
        FROM bike_metrics
        WHERE session_id = :id
        ORDER BY idx
    """)
    metrics_result = await db.execute(metrics_sql, {"id": session_id})
    metrics_rows = metrics_result.mappings().all()

    return BikeSessionDetailOut(
        id=session["id"],
        workout_date=session["workout_date"],
        distance_km=float(session["distance_km"]) if session["distance_km"] is not None else None,
        duration_min=float(session["duration_min"]) if session["duration_min"] is not None else None,
        avg_speed_kmh=float(session["avg_speed_kmh"]) if session["avg_speed_kmh"] is not None else None,
        calories=session["calories"],
        notes=session["notes"],
        created_at=session["created_at"],
        metrics=[
            BikeMetricPoint(
                idx=m["idx"],
                speed=float(m["speed"]) if m["speed"] is not None else None,
                cadence=float(m["cadence"]) if m["cadence"] is not None else None,
                resistance=float(m["resistance"]) if m["resistance"] is not None else None,
                heart_rate=float(m["heart_rate"]) if m["heart_rate"] is not None else None,
            )
            for m in metrics_rows
        ],
    )
