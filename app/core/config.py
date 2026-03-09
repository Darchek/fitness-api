from pydantic_settings import BaseSettings
from typing import List
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str = ""
    SECRET_KEY: str = ""
    ALLOWED_ORIGINS: str = "*"

    @property
    def allowed_origins_list(self) -> List[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"


settings = Settings()
