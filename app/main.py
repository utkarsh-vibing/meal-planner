from fastapi import FastAPI

from app.api.routes import router
from app.config import get_settings
from app.db import create_db_and_tables

settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(router, prefix=settings.api_prefix)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()
