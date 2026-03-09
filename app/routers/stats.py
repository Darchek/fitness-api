from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db.session import get_db

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("")
async def get_stats(db: AsyncSession = Depends(get_db)):
    # Totals
    totals = await db.execute(text("""
        SELECT
            (SELECT COUNT(*) FROM cardio_workouts) AS total_cardio,
            (SELECT COUNT(*) FROM strength_workouts) AS total_strength,
            (SELECT COALESCE(SUM(distance_km), 0) FROM cardio_workouts) AS total_distance,
            (SELECT COALESCE(SUM(calories), 0) FROM cardio_workouts) AS total_calories
    """))
    t = totals.mappings().first()

    # Most active day
    mad = await db.execute(text("""
        SELECT workout_date::text AS day, COUNT(*) AS cnt
        FROM (
            SELECT workout_date FROM cardio_workouts
            UNION ALL
            SELECT workout_date FROM strength_workouts
        ) combined
        GROUP BY workout_date
        ORDER BY cnt DESC
        LIMIT 1
    """))
    mad_row = mad.mappings().first()

    # Weekly activity (last 84 days by week)
    weekly = await db.execute(text("""
        SELECT
            date_trunc('week', workout_date)::date::text AS week,
            COUNT(*) AS total,
            SUM(CASE WHEN kind = 'cardio' THEN 1 ELSE 0 END) AS cardio,
            SUM(CASE WHEN kind = 'strength' THEN 1 ELSE 0 END) AS strength
        FROM (
            SELECT workout_date, 'cardio' AS kind FROM cardio_workouts
            WHERE workout_date >= CURRENT_DATE - INTERVAL '84 days'
            UNION ALL
            SELECT workout_date, 'strength' AS kind FROM strength_workouts
            WHERE workout_date >= CURRENT_DATE - INTERVAL '84 days'
        ) combined
        GROUP BY date_trunc('week', workout_date)
        ORDER BY week
    """))
    weekly_rows = [dict(r) for r in weekly.mappings().all()]

    # Recent workouts (10)
    recent = await db.execute(text("""
        SELECT id, workout_date, type AS activity, 'cardio' AS category,
               distance_km, duration_min, calories
        FROM cardio_workouts
        UNION ALL
        SELECT id, workout_date, exercise AS activity, 'strength' AS category,
               NULL, NULL, NULL
        FROM strength_workouts
        ORDER BY workout_date DESC
        LIMIT 10
    """))
    recent_rows = [dict(r) for r in recent.mappings().all()]

    # Cardio by type
    cardio_by_type = await db.execute(text("""
        SELECT type as name, COUNT(*) AS count,
               COALESCE(SUM(distance_km), 0) AS total_km,
               COALESCE(SUM(calories), 0) AS total_cal
        FROM cardio_workouts
        GROUP BY type
        ORDER BY count DESC
    """))
    cardio_type_rows = [dict(r) for r in cardio_by_type.mappings().all()]

    # Strength by exercise
    strength_by_exercise = await db.execute(text("""
        SELECT exercise AS name, COUNT(*) AS count,
               COALESCE(SUM(total_reps), 0) AS total_reps
        FROM strength_workouts
        GROUP BY exercise
        ORDER BY count DESC
    """))
    strength_exercise_rows = [dict(r) for r in strength_by_exercise.mappings().all()]

    # Cardio over time (last 60 days)
    cardio_over_time = await db.execute(text("""
        SELECT workout_date AS date, COUNT(*) AS count,
               COALESCE(SUM(distance_km), 0) AS distance_km,
               COALESCE(AVG(avg_speed_kmh), 0) AS avg_speed_kmh,
               COALESCE(SUM(calories), 0) AS calories,
               type
        FROM cardio_workouts
        WHERE workout_date >= CURRENT_DATE - INTERVAL '60 days'
        GROUP BY workout_date, type
        ORDER BY workout_date
    """))
    cardio_time_rows = [dict(r) for r in cardio_over_time.mappings().all()]

    # Workout days (per-date categories)
    workout_days = await db.execute(text("""
        SELECT DATE(combined.day) AS day,
               array_agg(DISTINCT kind) AS categories
        FROM (
            SELECT event_date AS day, habit AS kind FROM habit_logs
            UNION ALL
            SELECT workout_date AS day, 'cardio' AS kind FROM cardio_workouts
            UNION ALL
            SELECT workout_date AS day, 'strength' AS kind FROM strength_workouts
        ) combined
        GROUP BY DATE(combined.day)
        ORDER BY DATE(combined.day) ASC
    """))
    workout_day_rows = [dict(r) for r in workout_days.mappings().all()]

    total_cardio = t["total_cardio"]
    total_strength = t["total_strength"]

    return {
        "totalCardio": total_cardio,
        "totalStrength": total_strength,
        "totalWorkouts": total_cardio + total_strength,
        "totalDistance": float(t["total_distance"]),
        "totalCalories": float(t["total_calories"]),
        "mostActiveDay": datetime.fromisoformat(mad_row["day"]).strftime("%A") if mad_row else None,
        "weeklyActivity": [
            {**r, "label": r["week"][5:].replace("-", "/"), "total": int(r["total"]), "cardio": int(r["cardio"]), "strength": int(r["strength"])}
            for r in weekly_rows
        ],
        "recentWorkouts": [
            {**r, "workout_date": r["workout_date"].isoformat(), "distance_km": float(r["distance_km"]) if r.get("distance_km") is not None else None,
             "category": r["category"], "duration_min": float(r["duration_min"]) if r.get("duration_min") is not None else None}
            for r in recent_rows
        ],
        "cardioByType": [
            {**r, "value": int(r["count"]), "total_km": float(r["total_km"]),
             "total_cal": float(r["total_cal"])}
            for r in cardio_type_rows
        ],
        "strengthByExercise": [
            {**r, "value": int(r["count"]), "total_reps": int(r["total_reps"])}
            for r in strength_exercise_rows
        ],
        "cardioOverTime": [
            {**r, "date": r["date"].strftime("%Y-%m-%d"), "distance_km": float(r["distance_km"])}
            for r in cardio_time_rows
        ],
        "workoutDays": [
            {**r, "day": r["day"].strftime("%Y-%m-%d"), "categories": ",".join(r["categories"]) }
            for r in workout_day_rows],
    }
