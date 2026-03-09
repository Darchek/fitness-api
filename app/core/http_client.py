import asyncio

import requests
from app.core.config import settings
import logging

from app.schemas.cardio import CardioBikeSessionCreate

log = logging.getLogger(__name__)

class HttpClient:


    @staticmethod
    async def send_n8n_start_bike_session():
        try:
            response = requests.get(f"{settings.N8N_WEBHOOK_URL}/bike/start")
            res = response.json()
            log.info(res)
            return True
        except Exception as e:
            log.error(f"Request error: {e}")
            return False

    @staticmethod
    async def send_n8n_end_bike_session(payload: dict):
        try:
            response = requests.post(f"{settings.N8N_WEBHOOK_URL}/bike/end", json=payload)
            res = response.json()
            log.info(res)
            return True
        except Exception as e:
            log.error(f"Request error: {e}")
            return False
