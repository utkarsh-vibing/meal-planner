from datetime import date

from sqlmodel import Session, select

from app.models import Meal, MealPlan, MealPlanSlot, MealTime


def generate_week_plan(session: Session, user_id: int, week_start_date: date) -> MealPlan:
    meals = session.exec(select(Meal).where(Meal.user_id == user_id)).all()
    plan = MealPlan(user_id=user_id, week_start_date=week_start_date)
    session.add(plan)
    session.flush()

    meal_times = [MealTime.breakfast, MealTime.lunch, MealTime.dinner, MealTime.snack]
    meal_ids = [meal.id for meal in meals if meal.id is not None]
    for day in range(7):
        for idx, meal_time in enumerate(meal_times):
            meal_id = meal_ids[(day + idx) % len(meal_ids)] if meal_ids else None
            slot = MealPlanSlot(
                meal_plan_id=plan.id,
                day=day,
                meal_time=meal_time,
                meal_id=meal_id,
            )
            session.add(slot)

    session.commit()
    session.refresh(plan)
    return plan
