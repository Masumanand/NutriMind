from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta, date

from database import get_db
from models.user import User
from models.food import FoodLog, WaterLog, WeightLog
from models.streak import MealPhotoStreak
from services.auth_service import get_current_user

router = APIRouter()


@router.get("/dashboard")
async def get_health_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Full health dashboard data."""
    today_start = datetime.now().replace(hour=0, minute=0, second=0)
    week_start = datetime.now() - timedelta(days=7)

    # Today's food logs
    today_logs_result = await db.execute(
        select(FoodLog).where(
            and_(FoodLog.user_id == current_user.id, FoodLog.logged_at >= today_start)
        )
    )
    today_logs = today_logs_result.scalars().all()

    # Today's water
    water_result = await db.execute(
        select(func.sum(WaterLog.amount_ml)).where(
            and_(WaterLog.user_id == current_user.id, WaterLog.logged_at >= today_start)
        )
    )
    water_today_ml = water_result.scalar() or 0

    # Weekly calorie trend (last 7 days)
    weekly_result = await db.execute(
        select(
            func.date(FoodLog.logged_at).label("day"),
            func.sum(FoodLog.calories).label("total_calories"),
        ).where(
            and_(FoodLog.user_id == current_user.id, FoodLog.logged_at >= week_start)
        ).group_by(func.date(FoodLog.logged_at)).order_by(func.date(FoodLog.logged_at))
    )
    weekly_calories = [{"date": str(r.day), "calories": round(r.total_calories or 0, 1)} for r in weekly_result.all()]

    # Latest weight
    weight_result = await db.execute(
        select(WeightLog).where(WeightLog.user_id == current_user.id)
        .order_by(WeightLog.logged_at.desc()).limit(1)
    )
    latest_weight = weight_result.scalar_one_or_none()

    # Today's macros
    today_calories = sum(l.calories or 0 for l in today_logs)
    today_protein = sum(l.protein or 0 for l in today_logs)
    today_carbs = sum(l.carbs or 0 for l in today_logs)
    today_fat = sum(l.fat or 0 for l in today_logs)

    calorie_target = current_user.daily_calorie_target or 2000

    # Meal photo streak
    today_date = date.today()
    streak_result = await db.execute(
        select(MealPhotoStreak).where(
            and_(
                MealPhotoStreak.user_id == current_user.id,
                MealPhotoStreak.date == today_date,
            )
        )
    )
    streak_record = streak_result.scalar_one_or_none()

    return {
        "user": {
            "name": current_user.full_name or current_user.username,
            "level": current_user.level,
            "points": current_user.total_points,
            "streak": current_user.current_streak,
            "longest_streak": current_user.longest_streak or 0,
            "goal": current_user.goal.value if current_user.goal else None,
        },
        "today": {
            "calories": round(today_calories, 1),
            "calorie_target": calorie_target,
            "calorie_pct": round(today_calories / calorie_target * 100, 1),
            "protein": round(today_protein, 1),
            "carbs": round(today_carbs, 1),
            "fat": round(today_fat, 1),
            "water_ml": round(water_today_ml, 0),
            "water_target_ml": (current_user.daily_water_target or 2.5) * 1000,
            "meals_logged": len(today_logs),
        },
        "meal_streak": {
            "current_streak": current_user.current_streak,
            "breakfast": streak_record.breakfast_logged if streak_record else False,
            "lunch": streak_record.lunch_logged if streak_record else False,
            "dinner": streak_record.dinner_logged if streak_record else False,
            "day_complete": streak_record.day_complete if streak_record else False,
        },
        "weight": {
            "current": latest_weight.weight_kg if latest_weight else current_user.weight_kg,
            "target": current_user.target_weight_kg,
            "last_logged": latest_weight.logged_at.isoformat() if latest_weight else None,
        },
        "weekly_calories": weekly_calories,
        "targets": {
            "calories": calorie_target,
            "protein": current_user.daily_protein_target or 50,
            "carbs": current_user.daily_carb_target or 250,
            "fat": current_user.daily_fat_target or 65,
            "water_ml": (current_user.daily_water_target or 2.5) * 1000,
        },
    }
