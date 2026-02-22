from app.db import get_conn


def summarize_grocery(user_id: int) -> list[dict]:
    with get_conn() as conn:
        plan = conn.execute(
            "SELECT id FROM meal_plans WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,)
        ).fetchone()
        if not plan:
            return []

        rows = conn.execute(
            """
            SELECT i.canonical_name AS ingredient_name, i.category, mi.unit, SUM(mi.quantity) AS quantity
            FROM meal_plan_slots s
            JOIN meal_ingredients mi ON mi.meal_id = s.meal_id
            JOIN ingredients i ON i.id = mi.ingredient_id
            WHERE s.meal_plan_id = ?
            GROUP BY i.canonical_name, i.category, mi.unit
            ORDER BY i.canonical_name
            """,
            (plan["id"],),
        ).fetchall()

        return [
            {
                "ingredient_name": r["ingredient_name"],
                "quantity": round(float(r["quantity"]), 2),
                "unit": r["unit"],
                "category": r["category"],
            }
            for r in rows
        ]
