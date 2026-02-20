from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class MealTime(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class GroceryScope(str, Enum):
    tomorrow = "tomorrow"
    this_week = "this_week"
    next_week = "next_week"


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    dietary_preferences: str | None = None
    metric_preference: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    meals: list[Meal] = Relationship(back_populates="user")


class Ingredient(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    canonical_name: str = Field(index=True)
    aliases: str = ""
    unit_default: str = "unit"
    category: str = "pantry"


class Meal(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    name: str = Field(index=True)
    prep_notes: str | None = None
    youtube_url: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    user: User | None = Relationship(back_populates="meals")
    ingredients: list[MealIngredient] = Relationship(back_populates="meal")


class MealIngredient(SQLModel, table=True):
    meal_id: int = Field(foreign_key="meal.id", primary_key=True)
    ingredient_id: int = Field(foreign_key="ingredient.id", primary_key=True)
    quantity: float = 1.0
    unit: str = "unit"

    meal: Meal | None = Relationship(back_populates="ingredients")


class DietPlan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    name: str = Field(index=True)
    source_text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MealPlan(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    week_start_date: date = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    slots: list[MealPlanSlot] = Relationship(back_populates="meal_plan")


class MealPlanSlot(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    meal_plan_id: int = Field(foreign_key="mealplan.id", index=True)
    day: int = Field(ge=0, le=6)
    meal_time: MealTime
    meal_id: int | None = Field(default=None, foreign_key="meal.id")

    meal_plan: MealPlan | None = Relationship(back_populates="slots")


class PantryItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    ingredient_id: int = Field(foreign_key="ingredient.id", index=True)
    have_it: bool = False
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class GroceryList(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    scope: GroceryScope
    generated_at: datetime = Field(default_factory=datetime.utcnow)
