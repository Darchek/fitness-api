from __future__ import annotations

from datetime import datetime
from typing import List

from app.db.models import CardioWorkout
from app.db.models.bike_metrics import BikeMetric
from app.schemas.cardio import BikeWorkoutByDateResponse, BikeWorkoutSummary


def build_bike_workout_by_date_response(
    workout: CardioWorkout,
    sample_every_seconds: int = 5,
    sample_every_points: int = 10,
) -> BikeWorkoutByDateResponse:
    sampled_metrics = sample_metrics(
        workout.metrics,
        sample_every_seconds=sample_every_seconds,
        sample_every_points=sample_every_points,
    )
    summary = build_workout_summary(workout, sampled_metrics)

    return BikeWorkoutByDateResponse(
        **{
            **workout.__dict__,
            "summary": summary,
            "metrics": sampled_metrics,
        }
    )


def sample_metrics(
    metrics: List[BikeMetric],
    sample_every_seconds: int = 2,
    sample_every_points: int = 10,
) -> List[BikeMetric]:
    if len(metrics) <= 6:
        return list(metrics)

    selected_by_idx = {}

    def add_metric(metric: BikeMetric | None):
        if metric is not None:
            selected_by_idx[metric.idx] = metric

    for metric in _downsample_metrics(metrics, sample_every_seconds, sample_every_points):
        add_metric(metric)

    checkpoints = [
        metrics[0],
        metrics[len(metrics) // 4],
        metrics[len(metrics) // 2],
        metrics[(len(metrics) * 3) // 4],
        metrics[-1],
    ]
    for metric in checkpoints:
        add_metric(metric)

    add_metric(metric_with_max(metrics, "speed"))
    add_metric(metric_with_max(metrics, "heart_rate"))
    add_metric(metric_with_max(metrics, "cadence"))
    add_metric(metric_with_max(metrics, "resistance"))

    return sorted(selected_by_idx.values(), key=lambda metric: metric.idx)


def _downsample_metrics(
    metrics: List[BikeMetric],
    sample_every_seconds: int,
    sample_every_points: int,
) -> List[BikeMetric]:
    if _has_valid_timestamps(metrics):
        return _sample_by_time_window(metrics, sample_every_seconds)
    return _sample_by_point_stride(metrics, sample_every_points)


def _has_valid_timestamps(metrics: List[BikeMetric]) -> bool:
    return all(metric.measured_at is not None for metric in metrics)


def _sample_by_time_window(metrics: List[BikeMetric], sample_every_seconds: int) -> List[BikeMetric]:
    if sample_every_seconds <= 0:
        return list(metrics)

    sampled = []
    bucket_start = metrics[0].measured_at
    current_bucket = []

    for metric in metrics:
        if bucket_start is None or metric.measured_at is None:
            continue

        elapsed_seconds = (metric.measured_at - bucket_start).total_seconds()
        if elapsed_seconds >= sample_every_seconds and current_bucket:
            sampled.append(_representative_metric(current_bucket))
            bucket_start = metric.measured_at
            current_bucket = [metric]
            continue

        current_bucket.append(metric)

    if current_bucket:
        sampled.append(_representative_metric(current_bucket))

    return sampled


def _sample_by_point_stride(metrics: List[BikeMetric], sample_every_points: int) -> List[BikeMetric]:
    if sample_every_points <= 1:
        return list(metrics)
    return metrics[::sample_every_points]


def _representative_metric(bucket: List[BikeMetric]) -> BikeMetric:
    middle_idx = len(bucket) // 2
    return bucket[middle_idx]


def metric_with_max(metrics: List[BikeMetric], field_name: str) -> BikeMetric | None:
    valid_metrics = [metric for metric in metrics if getattr(metric, field_name) is not None]
    if not valid_metrics:
        return None
    return max(valid_metrics, key=lambda metric: getattr(metric, field_name))


def average(metrics: List[BikeMetric], field_name: str) -> float | None:
    values = [getattr(metric, field_name) for metric in metrics if getattr(metric, field_name) is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 2)


def maximum(metrics: List[BikeMetric], field_name: str) -> float | int | None:
    values = [getattr(metric, field_name) for metric in metrics if getattr(metric, field_name) is not None]
    if not values:
        return None
    return max(values)


def build_workout_summary(workout: CardioWorkout, sampled_metrics: List[BikeMetric]) -> BikeWorkoutSummary:
    metrics = list(workout.metrics)
    avg_speed = average(metrics, "speed")
    max_speed = maximum(metrics, "speed")
    avg_cadence = average(metrics, "cadence")
    max_cadence = maximum(metrics, "cadence")
    avg_resistance = average(metrics, "resistance")
    max_resistance = maximum(metrics, "resistance")
    avg_heart_rate = average(metrics, "heart_rate")
    max_heart_rate = maximum(metrics, "heart_rate")

    summary_parts = []
    if workout.duration_min is not None:
        summary_parts.append(f"{round(workout.duration_min, 1)} min")
    if workout.distance_km is not None:
        summary_parts.append(f"{round(workout.distance_km, 2)} km")
    if avg_speed is not None:
        summary_parts.append(f"avg speed {avg_speed} km/h")
    if max_heart_rate is not None:
        summary_parts.append(f"peak HR {max_heart_rate} bpm")
    if max_cadence is not None:
        summary_parts.append(f"peak cadence {max_cadence} rpm")

    summary_text = "Cycling workout"
    if summary_parts:
        summary_text += ": " + ", ".join(summary_parts)
    summary_text += f". Timeline condensed to {len(sampled_metrics)} representative points."

    return BikeWorkoutSummary(
        total_points=len(metrics),
        sampled_points=len(sampled_metrics),
        avg_speed=avg_speed,
        max_speed=max_speed,
        avg_cadence=avg_cadence,
        max_cadence=max_cadence,
        avg_resistance=avg_resistance,
        max_resistance=max_resistance,
        avg_heart_rate=avg_heart_rate,
        max_heart_rate=max_heart_rate,
        summary_text=summary_text,
    )


def estimate_training_zone(avg_heart_rate: float | None, age: int = 32) -> str | None:
    if avg_heart_rate is None:
        return None

    max_heart_rate = 220 - age
    zone_2_min = max_heart_rate * 0.60
    zone_2_max = max_heart_rate * 0.70
    zone_3_max = max_heart_rate * 0.80

    if zone_2_min <= avg_heart_rate < zone_2_max:
        return "Zone 2"
    if zone_2_max <= avg_heart_rate < zone_3_max:
        return "Zone 3"
    if avg_heart_rate < zone_2_min:
        return "Below Zone 2"
    return "Above Zone 3"


def build_workout_payload_for_llm(workout_response: BikeWorkoutByDateResponse, age: int = 32) -> dict:
    workout_dict = workout_response.model_dump(mode="json")
    workout_dict["estimated_zone"] = estimate_training_zone(
        workout_response.summary.avg_heart_rate,
        age=age,
    )
    return workout_dict
