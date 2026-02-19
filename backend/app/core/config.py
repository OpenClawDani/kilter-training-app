from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str
    redis_url: str
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    environment: str = "development"

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
