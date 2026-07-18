from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
from openai import AsyncOpenAI
import json

from models.user import User
from services.auth_service import get_current_user
from config import settings

router = APIRouter()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class MealPlanRequest(BaseModel):
    days: int = Field(7, ge=1, le=14)
    budget_usd: Optional[float] = None
    exclude_ingredients: Optional[List[str]] = None
    cuisine_preference: Optional[str] = None


class GroceryListRequest(BaseModel):
    meal_plan: Optional[dict] = None
    budget_usd: Optional[float] = None
    servings: int = Field(1, ge=1, le=10)


@router.post("/meal-plan")
async def generate_meal_plan(
    data: MealPlanRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate a personalized weekly meal plan using AI."""
    budget_str = f"${data.budget_usd}/week" if data.budget_usd else "no constraint"
    cuisine_str = data.cuisine_preference or "any"
    exclude_str = ", ".join(data.exclude_ingredients or []) or "nothing"
    allergies_str = ", ".join(current_user.allergies or []) or "none"
    conditions_str = ", ".join(current_user.medical_conditions or []) or "none"

    prompt = f"""Generate a {data.days}-day meal plan for this user:
- Goal: {current_user.goal.value if current_user.goal else 'general health'}
- Diet: {current_user.diet_type.value if current_user.diet_type else 'omnivore'}
- Allergies: {allergies_str}
- Medical conditions: {conditions_str}
- Daily calorie target: {current_user.daily_calorie_target or 2000} kcal
- Budget: {budget_str}
- Cuisine preference: {cuisine_str}
- Exclude: {exclude_str}

Return JSON:
{{
  "meal_plan": {{
    "day_1": {{
      "breakfast": {{"name": "", "calories": 0, "prep_time_min": 0, "recipe_url": ""}},
      "lunch": {{"name": "", "calories": 0, "prep_time_min": 0, "recipe_url": ""}},
      "dinner": {{"name": "", "calories": 0, "prep_time_min": 0, "recipe_url": ""}},
      "snack": {{"name": "", "calories": 0, "prep_time_min": 0}}
    }}
  }},
  "total_daily_calories": 0,
  "estimated_weekly_cost_usd": 0,
  "nutrition_highlights": ["key benefit 1", "key benefit 2"],
  "tips": ["tip 1", "tip 2"]
}}"""

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=2000,
    )

    return json.loads(response.choices[0].message.content)


@router.post("/grocery-list")
async def generate_grocery_list(
    data: GroceryListRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate an optimized grocery list from meal plan."""
    allergies_str = ", ".join(current_user.allergies or []) or "none"
    budget_str = f"${data.budget_usd}" if data.budget_usd else "optimize for value"

    if data.meal_plan:
        context = f"Based on this meal plan: {json.dumps(data.meal_plan)}"
    else:
        context = (
            f"For a {current_user.diet_type.value if current_user.diet_type else 'omnivore'} diet, "
            f"goal: {current_user.goal.value if current_user.goal else 'general health'}, "
            f"{current_user.daily_calorie_target or 2000} kcal/day"
        )

    prompt = f"""Generate a weekly grocery list for {data.servings} person(s).
{context}
Budget: {budget_str}
Allergies to avoid: {allergies_str}

Return JSON:
{{
  "grocery_list": {{
    "produce": [{{"item": "", "quantity": "", "estimated_cost_usd": 0}}],
    "proteins": [],
    "grains": [],
    "dairy_alternatives": [],
    "pantry": [],
    "beverages": []
  }},
  "total_estimated_cost_usd": 0,
  "cost_saving_tips": ["tip 1", "tip 2"],
  "nutrition_notes": "brief note on nutritional balance"
}}"""

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=1500,
    )

    return json.loads(response.choices[0].message.content)


@router.get("/recommendations")
async def get_meal_recommendations(
    meal_type: str = "lunch",
    current_user: User = Depends(get_current_user),
):
    """Quick meal recommendations for right now."""
    allergies_str = ", ".join(current_user.allergies or []) or "none"
    meal_calories = (current_user.daily_calorie_target or 2000) // 3

    prompt = f"""Suggest 5 {meal_type} options for this user:
- Diet: {current_user.diet_type.value if current_user.diet_type else 'omnivore'}
- Goal: {current_user.goal.value if current_user.goal else 'general health'}
- Allergies: {allergies_str}
- Calorie target for this meal: {meal_calories} kcal

Return JSON:
{{
  "recommendations": [{{
    "name": "",
    "calories": 0,
    "protein_g": 0,
    "carbs_g": 0,
    "fat_g": 0,
    "prep_time_min": 0,
    "difficulty": "easy",
    "why_recommended": "explanation",
    "sustainability_score": 5
  }}]
}}"""

    response = await client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=800,
    )

    result = json.loads(response.choices[0].message.content)
    return result.get("recommendations", result)
