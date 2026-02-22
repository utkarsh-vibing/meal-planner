from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select

from app.db import get_session
from app.models import GroceryList, Ingredient, Meal, MealIngredient, MealPlan, MealPlanSlot
from app.schemas import GroceryRequest, MealCreate, PlanGenerateRequest, SlotUpdateRequest
from app.services.grocery import summarize_grocery_for_plan
from app.services.planner import generate_week_plan

router = APIRouter()


@router.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/meals")
def create_meal(payload: MealCreate, session: Session = Depends(get_session)) -> Meal:
    meal = Meal(
        user_id=payload.user_id,
        name=payload.name,
        prep_notes=payload.prep_notes,
        youtube_url=payload.youtube_url,
    )
    session.add(meal)
    session.flush()

    for ingredient_in in payload.ingredients:
        ingredient = session.exec(
            select(Ingredient).where(
                Ingredient.user_id == payload.user_id,
                Ingredient.canonical_name == ingredient_in.ingredient_name.lower().strip(),
            )
        ).first()
        if ingredient is None:
            ingredient = Ingredient(
                user_id=payload.user_id,
                canonical_name=ingredient_in.ingredient_name.lower().strip(),
                unit_default=ingredient_in.unit,
            )
            session.add(ingredient)
            session.flush()

        session.add(
            MealIngredient(
                meal_id=meal.id,
                ingredient_id=ingredient.id,
                quantity=ingredient_in.quantity,
                unit=ingredient_in.unit,
            )
        )

    session.commit()
    session.refresh(meal)
    return meal


@router.get("/meals")
def list_meals(user_id: int, session: Session = Depends(get_session)) -> list[Meal]:
    return session.exec(select(Meal).where(Meal.user_id == user_id)).all()


@router.post("/meal-plan/generate")
def generate_plan(payload: PlanGenerateRequest, session: Session = Depends(get_session)) -> MealPlan:
    return generate_week_plan(session, payload.user_id, payload.week_start_date)


@router.get("/meal-plan/{week_start}")
def get_meal_plan(week_start: str, user_id: int, session: Session = Depends(get_session)) -> MealPlan:
    plan = session.exec(
        select(MealPlan).where(MealPlan.user_id == user_id, MealPlan.week_start_date == week_start)
    ).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")
    return plan


@router.patch("/meal-plan/slot")
def update_slot(payload: SlotUpdateRequest, session: Session = Depends(get_session)) -> MealPlanSlot:
    slot = session.exec(
        select(MealPlanSlot).where(
            MealPlanSlot.meal_plan_id == payload.meal_plan_id,
            MealPlanSlot.day == payload.day,
            MealPlanSlot.meal_time == payload.meal_time,
        )
    ).first()
    if slot is None:
        raise HTTPException(status_code=404, detail="Slot not found")
    slot.meal_id = payload.meal_id
    session.add(slot)
    session.commit()
    session.refresh(slot)
    return slot


@router.post("/grocery-list")
def generate_grocery(payload: GroceryRequest, session: Session = Depends(get_session)) -> dict:
    latest_plan = session.exec(
        select(MealPlan).where(MealPlan.user_id == payload.user_id).order_by(MealPlan.id.desc())
    ).first()
    if latest_plan is None:
        raise HTTPException(status_code=400, detail="No meal plan available")

    items = summarize_grocery_for_plan(session, latest_plan.id)
    grocery = GroceryList(user_id=payload.user_id, scope=payload.scope)
    session.add(grocery)
    session.commit()

    return {
        "list_id": grocery.id,
        "scope": payload.scope,
        "items": items,
    }
