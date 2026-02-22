from dataclasses import dataclass
from enum import Enum


class MealTime(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    snack = "snack"


class GroceryScope(str, Enum):
    tomorrow = "tomorrow"
    this_week = "this_week"
    next_week = "next_week"


@dataclass
class User:
    id: int
    name: str
    dietary_preferences: str | None
    metric_preference: bool
