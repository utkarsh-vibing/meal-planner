from app.db import get_conn
from app.models import MealTime


MEAL_TIMES = [MealTime.breakfast.value, MealTime.lunch.value, MealTime.dinner.value, MealTime.snack.value]


def generate_week_plan(user_id: int, week_start_date: str) -> dict:
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id, user_id, week_start_date FROM meal_plans WHERE user_id = ? AND week_start_date = ?",
            (user_id, week_start_date),
        ).fetchone()
        if existing:
            return dict(existing)

        cur = conn.execute(
            "INSERT INTO meal_plans (user_id, week_start_date) VALUES (?, ?)",
            (user_id, week_start_date),
        )
        plan_id = cur.lastrowid

        meals = conn.execute("SELECT id FROM meals WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()
        meal_ids = [row["id"] for row in meals]

        for day in range(7):
            for idx, meal_time in enumerate(MEAL_TIMES):
                meal_id = meal_ids[(day + idx) % len(meal_ids)] if meal_ids else None
                conn.execute(
                    "INSERT INTO meal_plan_slots (meal_plan_id, day, meal_time, meal_id) VALUES (?, ?, ?, ?)",
                    (plan_id, day, meal_time, meal_id),
                )

        return {"id": plan_id, "user_id": user_id, "week_start_date": week_start_date}
