from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import cardio, strength, bike, workouts, weight, habits, stats, auth
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Fitness API", lifespan=lifespan, root_path="/api")

# CORS
origins = settings.allowed_origins_list
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workouts.router)
app.include_router(bike.router)
app.include_router(cardio.router)
app.include_router(strength.router)
app.include_router(stats.router)
app.include_router(weight.router)
app.include_router(habits.router)
app.include_router(auth.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=18110)