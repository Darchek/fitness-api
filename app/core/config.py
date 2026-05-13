from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    ALLOWED_ORIGINS: str = "*"
    N8N_WEBHOOK_URL: str = ""
    N8N_WEBHOOK_URL_DEV: str = ""
    STRAVA_TOKEN: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = ""

    @property
    def allowed_origins_list(self) -> List[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
