from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MealMind API"
    app_env: str = "dev"
    database_url: str = Field(default="sqlite:///./mealmind.db")
    api_prefix: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="MEALMIND_")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
