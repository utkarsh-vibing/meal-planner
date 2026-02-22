from collections import defaultdict

from sqlmodel import Session, select

from app.models import MealIngredient, MealPlanSlot


def summarize_grocery_for_plan(session: Session, meal_plan_id: int) -> dict[str, float]:
    slots = session.exec(select(MealPlanSlot).where(MealPlanSlot.meal_plan_id == meal_plan_id)).all()
    totals: dict[str, float] = defaultdict(float)
    for slot in slots:
        if not slot.meal_id:
            continue
        meal_ingredients = session.exec(
            select(MealIngredient).where(MealIngredient.meal_id == slot.meal_id)
        ).all()
        for row in meal_ingredients:
            key = f"ingredient_{row.ingredient_id}:{row.unit}"
            totals[key] += row.quantity
    return dict(totals)
