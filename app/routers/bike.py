from datetime import date, datetime
import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.http_client import HttpClient
from app.prompts.gemini_prompts import build_weight_loss_bike_prompt
from app.services.gemini_service import GeminiService
from app.schemas.cardio import (
    BikeSessionListOut,
    CardioWorkoutResponse,
    CardioBikeSessionCreate,
    BikeWorkoutByDateResponse,
    BikeWorkoutLlmSummaryResponse,
)
from app.db.models import CardioWorkout
from app.db.models.bike_metrics import BikeMetric
from app.repositories.bike_repository import (
    create_cycling_session,
    get_cycling_session_by_date,
    get_cycling_session_by_id,
    list_cycling_sessions,
)
from app.db.session import get_db
from app.services.bike_service import (
    build_bike_workout_by_date_response,
    build_workout_payload_for_llm,
    estimate_training_zone,
)

router = APIRouter(prefix="/bike", tags=["bike"])
log = logging.getLogger(__name__)


def _limit_to_five_lines(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines[:5])


async def _generate_bike_llm_analysis(
    workout: CardioWorkout,
    sample_every_seconds: int = 5,
    sample_every_points: int = 10,
) -> BikeWorkoutLlmSummaryResponse:
    workout_response = build_bike_workout_by_date_response(
        workout,
        sample_every_seconds=sample_every_seconds,
        sample_every_points=sample_every_points,
    )
    workout_payload = build_workout_payload_for_llm(workout_response, age=32)
    prompt = build_weight_loss_bike_prompt(workout_payload)
    analysis = await GeminiService.generate_text(prompt)
    limited_analysis = _limit_to_five_lines(analysis)

    return BikeWorkoutLlmSummaryResponse(
        workout_date=workout_response.workout_date,
        estimated_zone=estimate_training_zone(workout_response.summary.avg_heart_rate, age=32),
        sampled_points=workout_response.summary.sampled_points,
        analysis=limited_analysis,
    )


@router.get("", response_model=List[BikeSessionListOut])
async def list_bike_sessions(
    limit: int = Query(200),
    db: AsyncSession = Depends(get_db),
):
    rows = await list_cycling_sessions(db, limit=limit)
    return [BikeSessionListOut(**dict(row)) for row in rows]

@router.get("/start")
async def start_bike_session():
    await HttpClient.send_n8n_start_bike_session()
    return "OK"

@router.get("/summary", response_model=BikeWorkoutLlmSummaryResponse)
async def get_bike_summary(
    workout_date: date | None = Query(None, description="Workout date in YYYY-MM-DD format"),
    sample_every_seconds: int = Query(5, ge=1, description="Keep one representative metric every N seconds"),
    sample_every_points: int = Query(10, ge=1, description="Fallback stride when timestamps are unavailable"),
    db: AsyncSession = Depends(get_db),
):
    effective_workout_date = workout_date or datetime.now().date()
    workout = await get_cycling_session_by_date(db, effective_workout_date)

    if workout is None:
        raise HTTPException(status_code=404, detail="Cycling workout not found for the requested date")

    try:
        return await _generate_bike_llm_analysis(
            workout,
            sample_every_seconds=sample_every_seconds,
            sample_every_points=sample_every_points,
        )
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Gemini request failed: {exc}")

@router.get("/by-date", response_model=BikeWorkoutByDateResponse)
async def get_bike_session_by_date(
    workout_date: date | None = Query(None, description="Workout date in YYYY-MM-DD format"),
    sample_every_seconds: int = Query(5, ge=1, description="Keep one representative metric every N seconds"),
    sample_every_points: int = Query(10, ge=1, description="Fallback stride when timestamps are unavailable"),
    db: AsyncSession = Depends(get_db),
):
    effective_workout_date = workout_date or datetime.now().date()
    workout = await get_cycling_session_by_date(db, effective_workout_date)

    if workout is None:
        raise HTTPException(status_code=404, detail="Cycling workout not found for the requested date")

    return build_bike_workout_by_date_response(
        workout,
        sample_every_seconds=sample_every_seconds,
        sample_every_points=sample_every_points,
    )


@router.get("/{_id}", response_model=CardioWorkoutResponse)
async def get_bike_session(_id: int, db: AsyncSession = Depends(get_db)):
    return await get_cycling_session_by_id(db, _id)

@router.post("", response_model=CardioWorkoutResponse)
async def create_bike_session(payload: CardioBikeSessionCreate, db: AsyncSession = Depends(get_db)):
    workout = CardioWorkout(
        **payload.model_dump(exclude={"metrics"}),
        metrics=[BikeMetric(**m.model_dump()) for m in payload.metrics]
    )
    workout = await create_cycling_session(db, workout)
    await HttpClient.send_n8n_end_bike_session(payload.model_dump(mode="json"))
    saved_workout = await get_cycling_session_by_id(db, workout.id)

    if saved_workout is not None:
        try:
            llm_summary = await _generate_bike_llm_analysis(saved_workout)
            await HttpClient.send_n8n_msg(llm_summary.analysis)
        except Exception as exc:
            log.error(f"Post-create bike analysis failed: {exc}")

    return saved_workout




"""
    data = {
        "type": "cycling",
        "workout_date": "2026-03-19T22:30:46.202Z",
        "distance_km": 10,
        "duration_min": 10,
        "avg_speed_kmh": 10,
        "calories": 120,
        "notes": "",
        "metrics": [
            {"idx": 1, "speed": 10.11, "distance": 12.23, "cadence": 23, "resistance": 2, "heart_rate": 120,
                "calories": 12},
            {"idx": 2, "speed": 10.12, "distance": 12.23, "cadence": 23, "resistance": 2, "heart_rate": 120,
                "calories": 12},
            {"idx": 3, "speed": 10.13, "distance": 12.23, "cadence": 23, "resistance": 2, "heart_rate": 120,
                "calories": 12}
        ]
    }
"""
