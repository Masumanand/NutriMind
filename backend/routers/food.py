from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, datetime, timedelta
from typing import List, Optional
from uuid import UUID

from database import get_db, get_mongo
from models.user import User
from models.food import FoodLog, FoodItem, WaterLog, WeightLog
from models.streak import MealPhotoStreak
from schemas.food import (
    FoodLogCreate, FoodLogResponse, DailySummary,
    WaterLogCreate, WeightLogCreate, FoodSearchResult
)
from services.auth_service import get_current_user
from services.nutrition_service import calculate_nutrition, get_daily_alerts

router = APIRouter()


@router.post("/log", response_model=FoodLogResponse, status_code=201)
async def log_food(
    data: FoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    nutrition = await calculate_nutrition(data.food_name, data.food_item_id, data.quantity_g, db)

    log = FoodLog(
        user_id=current_user.id,
        food_item_id=data.food_item_id,
        food_name=data.food_name,
        meal_type=data.meal_type,
        quantity_g=data.quantity_g,
        mood=data.mood,
        notes=data.notes,
        logged_via=data.logged_via,
        **nutrition,
    )
    db.add(log)
    await db.flush()
    await db.refresh(log)

    # Auto-update meal photo streak if logged via scanner/image
    if data.logged_via in ("scanner", "image") and data.meal_type in ("breakfast", "lunch", "dinner"):
        today = date.today()
        result = await db.execute(
            select(MealPhotoStreak).where(
                and_(
                    MealPhotoStreak.user_id == current_user.id,
                    MealPhotoStreak.date == today,
                )
            )
        )
        streak_record = result.scalar_one_or_none()
        if not streak_record:
            streak_record = MealPhotoStreak(user_id=current_user.id, date=today)
            db.add(streak_record)
            await db.flush()

        if data.meal_type == "breakfast":
            streak_record.breakfast_logged = True
        elif data.meal_type == "lunch":
            streak_record.lunch_logged = True
        elif data.meal_type == "dinner":
            streak_record.dinner_logged = True

        was_complete = streak_record.day_complete
        streak_record.day_complete = (
            streak_record.breakfast_logged and streak_record.lunch_logged and streak_record.dinner_logged
        )

        if streak_record.day_complete and not was_complete:
            current_user.total_points += 50
            db.add(current_user)

        db.add(streak_record)

    return FoodLogResponse.model_validate(log)


@router.get("/log/today", response_model=DailySummary)
async def get_today_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())

    result = await db.execute(
        select(FoodLog).where(
            and_(FoodLog.user_id == current_user.id, FoodLog.logged_at.between(start, end))
        )
    )
    logs = result.scalars().all()

    # Aggregate
    totals = {
        "total_calories": sum(l.calories or 0 for l in logs),
        "total_protein": sum(l.protein or 0 for l in logs),
        "total_carbs": sum(l.carbs or 0 for l in logs),
        "total_fat": sum(l.fat or 0 for l in logs),
        "total_fiber": sum(l.fiber or 0 for l in logs),
        "total_sugar": sum(l.sugar or 0 for l in logs),
    }

    # Water
    water_result = await db.execute(
        select(func.sum(WaterLog.amount_ml)).where(
            and_(WaterLog.user_id == current_user.id, WaterLog.logged_at.between(start, end))
        )
    )
    water_ml = water_result.scalar() or 0

    # Group by meal
    meals: dict = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
    for log in logs:
        meals[log.meal_type].append(FoodLogResponse.model_validate(log))

    # Health score (simple heuristic)
    calorie_ratio = totals["total_calories"] / max(current_user.daily_calorie_target or 2000, 1)
    health_score = max(0, min(100, 100 - abs(1 - calorie_ratio) * 50))

    alerts = get_daily_alerts(totals, current_user, water_ml)

    return DailySummary(
        date=str(today),
        **totals,
        water_ml=water_ml,
        calorie_target=current_user.daily_calorie_target or 2000,
        protein_target=current_user.daily_protein_target or 50,
        carb_target=current_user.daily_carb_target or 250,
        fat_target=current_user.daily_fat_target or 65,
        water_target_ml=(current_user.daily_water_target or 2.5) * 1000,
        meals=meals,
        health_score=round(health_score, 1),
        alerts=alerts,
    )


@router.get("/log/history")
async def get_food_history(
    days: int = Query(7, ge=1, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now() - timedelta(days=days)
    result = await db.execute(
        select(FoodLog).where(
            and_(FoodLog.user_id == current_user.id, FoodLog.logged_at >= since)
        ).order_by(FoodLog.logged_at.desc())
    )
    logs = result.scalars().all()
    return [FoodLogResponse.model_validate(l) for l in logs]


@router.delete("/log/{log_id}", status_code=204)
async def delete_food_log(
    log_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FoodLog).where(and_(FoodLog.id == log_id, FoodLog.user_id == current_user.id))
    )
    log = result.scalar_one_or_none()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    await db.delete(log)


@router.post("/water", status_code=201)
async def log_water(
    data: WaterLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = WaterLog(user_id=current_user.id, amount_ml=data.amount_ml)
    db.add(log)
    return {"message": "Water logged", "amount_ml": data.amount_ml}


@router.post("/weight", status_code=201)
async def log_weight(
    data: WeightLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    log = WeightLog(
        user_id=current_user.id,
        weight_kg=data.weight_kg,
        body_fat_pct=data.body_fat_pct,
        notes=data.notes,
    )
    db.add(log)
    # Update user's current weight
    current_user.weight_kg = data.weight_kg
    db.add(current_user)
    return {"message": "Weight logged", "weight_kg": data.weight_kg}


@router.get("/weight/history")
async def get_weight_history(
    days: int = Query(30, ge=7, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    since = datetime.now() - timedelta(days=days)
    result = await db.execute(
        select(WeightLog).where(
            and_(WeightLog.user_id == current_user.id, WeightLog.logged_at >= since)
        ).order_by(WeightLog.logged_at)
    )
    logs = result.scalars().all()
    return [{"date": l.logged_at.date(), "weight_kg": l.weight_kg} for l in logs]


@router.get("/search", response_model=List[FoodSearchResult])
async def search_food(
    q: str = Query(min_length=2),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FoodItem).where(FoodItem.name.ilike(f"%{q}%")).limit(20)
    )
    items = result.scalars().all()
    return [FoodSearchResult(
        id=item.id,
        name=item.name,
        brand=item.brand,
        calories_per_100g=item.calories_per_100g,
        protein_per_100g=item.protein_per_100g,
        carbs_per_100g=item.carbs_per_100g,
        fat_per_100g=item.fat_per_100g,
        health_score=item.health_score,
        sustainability_score=item.sustainability_score,
        diet_tags=item.diet_tags or [],
        allergens=item.allergens or [],
    ) for item in items]
