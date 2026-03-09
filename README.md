# Fitness API

FastAPI backend for fitness tracking, backed by PostgreSQL.

## Setup

```bash
cp .env.example .env
# Edit .env with your database credentials

pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Docker

```bash
docker-compose up --build
```

API available at http://localhost:8001

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Health check |
| GET | /api/workouts | Union of cardio + strength |
| GET | /api/cardio | Cardio workouts |
| POST | /api/cardio | Create cardio workout |
| GET | /api/strength | Strength workouts |
| POST | /api/strength | Create strength workout |
| GET | /api/bike | Cycling sessions with metrics |
| GET | /api/bike/{id} | Single cycling session + metrics array |
| GET | /api/weight | Weight logs |
| GET | /api/habits | Habit logs |
| GET | /api/stats | Aggregated stats |
| POST | /api/auth | Authenticate user |
