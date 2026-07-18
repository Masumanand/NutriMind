from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID

from models.food import FoodItem
from models.user import User


async def calculate_nutrition(
    food_name: str,
    food_item_id: Optional[UUID],
    quantity_g: float,
    db: AsyncSession,
) -> dict:
    """Calculate nutrition for a given food and quantity."""
    item = None
    if food_item_id:
        result = await db.execute(select(FoodItem).where(FoodItem.id == food_item_id))
        item = result.scalar_one_or_none()

    if not item:
        # Fallback: search by name
        result = await db.execute(
            select(FoodItem).where(FoodItem.name.ilike(f"%{food_name}%")).limit(1)
        )
        item = result.scalar_one_or_none()

    if not item:
        # Use estimated values (average food)
        return {
            "calories": round(quantity_g * 1.5, 1),
            "protein": round(quantity_g * 0.05, 1),
            "carbs": round(quantity_g * 0.2, 1),
            "fat": round(quantity_g * 0.05, 1),
            "fiber": round(quantity_g * 0.02, 1),
            "sugar": round(quantity_g * 0.05, 1),
        }

    ratio = quantity_g / 100
    return {
        "calories": round(item.calories_per_100g * ratio, 1),
        "protein": round(item.protein_per_100g * ratio, 1),
        "carbs": round(item.carbs_per_100g * ratio, 1),
        "fat": round(item.fat_per_100g * ratio, 1),
        "fiber": round((item.fiber_per_100g or 0) * ratio, 1),
        "sugar": round((item.sugar_per_100g or 0) * ratio, 1),
    }


def get_daily_alerts(totals: dict, user: User, water_ml: float) -> list[str]:
    """Generate health alerts based on daily intake."""
    alerts = []
    calorie_target = user.daily_calorie_target or 2000
    water_target_ml = (user.daily_water_target or 2.5) * 1000

    if totals["total_sugar"] > 50:
        alerts.append("⚠️ High sugar intake today — consider cutting back on sweets")
    if totals["total_calories"] > calorie_target * 1.2:
        alerts.append("⚠️ You've exceeded your calorie target by 20%")
    if totals["total_calories"] < calorie_target * 0.5:
        alerts.append("⚠️ Very low calorie intake — make sure you're eating enough")
    if totals["total_protein"] < (user.daily_protein_target or 50) * 0.6:
        alerts.append("💪 Protein intake is low — add more lean protein to your meals")
    if water_ml < water_target_ml * 0.5:
        alerts.append("💧 You're under-hydrated — drink more water")
    if totals["total_fat"] > (user.daily_fat_target or 65) * 1.3:
        alerts.append("⚠️ High fat intake today")

    return alerts


def calculate_sustainability_score(food_item: FoodItem) -> float:
    """
    Simple sustainability heuristic based on food category.
    Lower environmental impact = higher score.
    """
    category_scores = {
        "vegetable": 9.0, "fruit": 8.5, "grain": 7.5, "legume": 8.0,
        "dairy": 5.0, "poultry": 4.5, "fish": 5.5, "beef": 2.0,
        "pork": 3.5, "processed": 3.0, "beverage": 6.0,
    }
    return category_scores.get(food_item.category or "", 5.0)
