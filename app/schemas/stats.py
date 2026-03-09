from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class StatsOut(BaseModel):
    totalCardio: int
    totalStrength: int
    totalWorkouts: int
    totalDistance: float
    totalCalories: float
    mostActiveDay: Optional[str]
    weeklyActivity: List[Dict[str, Any]]
    recentWorkouts: List[Dict[str, Any]]
    cardioByType: List[Dict[str, Any]]
    strengthByExercise: List[Dict[str, Any]]
    cardioOverTime: List[Dict[str, Any]]
    workoutDays: List[Dict[str, Any]]
