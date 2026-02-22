from app.db import get_conn
from app.services.grocery import summarize_grocery
from app.services.planner import generate_week_plan


def health() -> tuple[int, dict]:
    return 200, {"status": "ok"}


def create_user(payload: dict) -> tuple[int, dict]:
    name = payload.get("name")
    if not name:
        return 400, {"detail": "name is required"}

    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (name, dietary_preferences, metric_preference) VALUES (?, ?, ?)",
            (name, payload.get("dietary_preferences"), int(payload.get("metric_preference", True))),
        )
        user_id = cur.lastrowid

    return 200, {"id": user_id, "name": name}


def create_meal(payload: dict) -> tuple[int, dict]:
    user_id = payload.get("user_id")
    name = payload.get("name")
    if not user_id or not name:
        return 400, {"detail": "user_id and name are required"}

    with get_conn() as conn:
        user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            return 404, {"detail": "User not found"}

        cur = conn.execute(
            "INSERT INTO meals (user_id, name, prep_notes, youtube_url) VALUES (?, ?, ?, ?)",
            (user_id, name, payload.get("prep_notes"), payload.get("youtube_url")),
        )
        meal_id = cur.lastrowid

        for item in payload.get("ingredients", []):
            canonical_name = item["ingredient_name"].strip().lower()
            ingredient = conn.execute(
                "SELECT id FROM ingredients WHERE user_id = ? AND canonical_name = ?",
                (user_id, canonical_name),
            ).fetchone()
            if ingredient:
                ingredient_id = ingredient["id"]
            else:
                cur_ing = conn.execute(
                    "INSERT INTO ingredients (user_id, canonical_name, category) VALUES (?, ?, ?)",
                    (user_id, canonical_name, item.get("category", "pantry")),
                )
                ingredient_id = cur_ing.lastrowid

            conn.execute(
                "INSERT OR REPLACE INTO meal_ingredients (meal_id, ingredient_id, quantity, unit) VALUES (?, ?, ?, ?)",
                (meal_id, ingredient_id, float(item.get("quantity", 1)), item.get("unit", "unit")),
            )

    return 200, {"id": meal_id, "user_id": user_id, "name": name}


def list_meals(user_id: int) -> tuple[int, list[dict]]:
    with get_conn() as conn:
        rows = conn.execute("SELECT id, user_id, name FROM meals WHERE user_id = ? ORDER BY id", (user_id,)).fetchall()
    return 200, [dict(r) for r in rows]


def create_plan(payload: dict) -> tuple[int, dict]:
    user_id = payload.get("user_id")
    week_start_date = payload.get("week_start_date")
    if not user_id or not week_start_date:
        return 400, {"detail": "user_id and week_start_date are required"}

    with get_conn() as conn:
        user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        return 404, {"detail": "User not found"}

    return 200, generate_week_plan(user_id, week_start_date)


def get_plan(user_id: int, week_start_date: str) -> tuple[int, dict]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, user_id, week_start_date FROM meal_plans WHERE user_id = ? AND week_start_date = ?",
            (user_id, week_start_date),
        ).fetchone()
    if not row:
        return 404, {"detail": "Meal plan not found"}
    return 200, dict(row)


def update_slot(payload: dict) -> tuple[int, dict]:
    required = ["meal_plan_id", "day", "meal_time"]
    if any(k not in payload for k in required):
        return 400, {"detail": "meal_plan_id, day, and meal_time are required"}

    with get_conn() as conn:
        slot = conn.execute(
            "SELECT id FROM meal_plan_slots WHERE meal_plan_id = ? AND day = ? AND meal_time = ?",
            (payload["meal_plan_id"], payload["day"], payload["meal_time"]),
        ).fetchone()
        if not slot:
            return 404, {"detail": "Slot not found"}
        conn.execute("UPDATE meal_plan_slots SET meal_id = ? WHERE id = ?", (payload.get("meal_id"), slot["id"]))

    return 200, {"status": "updated"}


def grocery_list(payload: dict) -> tuple[int, dict]:
    user_id = payload.get("user_id")
    scope = payload.get("scope")
    if not user_id or not scope:
        return 400, {"detail": "user_id and scope are required"}

    items = summarize_grocery(user_id)
    if not items:
        return 400, {"detail": "No meal plan available"}

    return 200, {"scope": scope, "items": items}
