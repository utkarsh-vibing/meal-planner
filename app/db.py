import sqlite3
from contextlib import contextmanager

from app.config import get_settings


def _connect() -> sqlite3.Connection:
    settings = get_settings()
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_conn():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              dietary_preferences TEXT,
              metric_preference INTEGER NOT NULL DEFAULT 1
            );

            CREATE TABLE IF NOT EXISTS ingredients (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              canonical_name TEXT NOT NULL,
              category TEXT NOT NULL DEFAULT 'pantry',
              UNIQUE(user_id, canonical_name)
            );

            CREATE TABLE IF NOT EXISTS meals (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              name TEXT NOT NULL,
              prep_notes TEXT,
              youtube_url TEXT
            );

            CREATE TABLE IF NOT EXISTS meal_ingredients (
              meal_id INTEGER NOT NULL,
              ingredient_id INTEGER NOT NULL,
              quantity REAL NOT NULL,
              unit TEXT NOT NULL,
              PRIMARY KEY(meal_id, ingredient_id)
            );

            CREATE TABLE IF NOT EXISTS meal_plans (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              week_start_date TEXT NOT NULL,
              UNIQUE(user_id, week_start_date)
            );

            CREATE TABLE IF NOT EXISTS meal_plan_slots (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              meal_plan_id INTEGER NOT NULL,
              day INTEGER NOT NULL,
              meal_time TEXT NOT NULL,
              meal_id INTEGER,
              UNIQUE(meal_plan_id, day, meal_time)
            );
            """
        )
