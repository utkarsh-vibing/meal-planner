from datetime import date

from pydantic import BaseModel, Field

from app.models import GroceryScope, IngredientCategory, MealTime


class UserCreate(BaseModel):
    name: str
    dietary_preferences: str | None = None
    metric_preference: bool = True


class UserRead(BaseModel):
    id: int
    name: str
    dietary_preferences: str | None = None
    metric_preference: bool


class MealIngredientIn(BaseModel):
    ingredient_name: str
    quantity: float = 1.0
    unit: str = "unit"
    category: IngredientCategory = IngredientCategory.pantry


class MealCreate(BaseModel):
    user_id: int
    name: str
    prep_notes: str | None = None
    youtube_url: str | None = None
    ingredients: list[MealIngredientIn] = Field(default_factory=list)


class MealRead(BaseModel):
    id: int
    user_id: int
    name: str
    prep_notes: str | None = None
    youtube_url: str | None = None


class PlanGenerateRequest(BaseModel):
    user_id: int
    week_start_date: date


class SlotUpdateRequest(BaseModel):
    meal_plan_id: int
    day: int = Field(ge=0, le=6)
    meal_time: MealTime
    meal_id: int | None = None


class GroceryRequest(BaseModel):
    user_id: int
    scope: GroceryScope


class GroceryItemRead(BaseModel):
    ingredient_name: str
    quantity: float
    unit: str
    category: IngredientCategory


class GroceryListRead(BaseModel):
    list_id: int
    scope: GroceryScope
    items: list[GroceryItemRead]
