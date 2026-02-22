from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    app_name: str = "MealMind API"
    app_env: str = "dev"
    database_path: str = "mealmind.db"
    api_prefix: str = "/api/v1"


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("MEALMIND_APP_NAME", "MealMind API"),
        app_env=os.getenv("MEALMIND_APP_ENV", "dev"),
        database_path=os.getenv("MEALMIND_DATABASE_PATH", "mealmind.db"),
        api_prefix=os.getenv("MEALMIND_API_PREFIX", "/api/v1"),
    )
