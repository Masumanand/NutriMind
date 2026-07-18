from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from uuid import UUID
from datetime import datetime


class FoodLogCreate(BaseModel):
    food_name: str
    food_item_id: Optional[UUID] = None
    meal_type: str = Field(pattern="^(breakfast|lunch|dinner|snack)$")
    quantity_g: float = Field(gt=0)
    mood: Optional[str] = None
    notes: Optional[str] = None
    logged_via: str = "manual"


class FoodLogResponse(BaseModel):
    id: UUID
    food_name: str
    meal_type: str
    quantity_g: float
    calories: Optional[float]
    protein: Optional[float]
    carbs: Optional[float]
    fat: Optional[float]
    logged_at: datetime
    mood: Optional[str]

    class Config:
        from_attributes = True


class DailySummary(BaseModel):
    date: str
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fat: float
    total_fiber: float
    total_sugar: float
    water_ml: float
    calorie_target: int
    protein_target: float
    carb_target: float
    fat_target: float
    water_target_ml: float
    meals: Dict[str, List[FoodLogResponse]]
    health_score: float  # 0-100 for the day
    alerts: List[str]


class WaterLogCreate(BaseModel):
    amount_ml: float = Field(gt=0, le=5000)


class WeightLogCreate(BaseModel):
    weight_kg: float = Field(gt=20, le=500)
    body_fat_pct: Optional[float] = None
    notes: Optional[str] = None


class FoodSearchResult(BaseModel):
    id: Optional[UUID]
    name: str
    brand: Optional[str]
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    health_score: Optional[float]
    sustainability_score: Optional[float]
    diet_tags: List[str]
    allergens: List[str]
