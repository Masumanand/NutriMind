from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "NutriMind AI"
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://nutrimind:nutrimind@localhost:5432/nutrimind"
    MONGO_URL: str = "mongodb://localhost:27017/nutrimind"
    REDIS_URL: str = "redis://localhost:6379"

    # AI
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"]

    # External APIs
    WEATHER_API_KEY: str = ""
    SPOONACULAR_API_KEY: str = ""  # nutrition database

    class Config:
        env_file = ".env"


settings = Settings()
