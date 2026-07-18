from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime, timedelta, date
from typing import List

from database import get_db
from models.user import User
from models.food import FoodLog, WeightLog, WaterLog
from services.auth_service import get_current_user
from services.prediction_service import HealthPredictor

router = APIRouter()
predictor = HealthPredictor()


@router.get("/weekly-summary")
async def get_weekly_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Aggregated weekly nutrition insights."""
    since = datetime.now() - timedelta(days=7)
    result = await db.execute(
        select(FoodLog).where(
            and_(FoodLog.user_id == current_user.id, FoodLog.logged_at >= since)
        )
    )
    logs = result.scalars().all()

    if not logs:
        return {"message": "No data for this week", "insights": []}

    total_days = 7
    avg_calories = sum(l.calories or 0 for l in logs) / total_days
    avg_protein = sum(l.protein or 0 for l in logs) / total_days
    avg_carbs = sum(l.carbs or 0 for l in logs) / total_days
    avg_fat = sum(l.fat or 0 for l in logs) / total_days
    avg_sugar = sum(l.sugar or 0 for l in logs) / total_days

    calorie_target = current_user.daily_calorie_target or 2000

    insights = []
    if avg_sugar > 40:
        insights.append({"type": "warning", "message": "You're eating too much sugar this week", "icon": "🍬"})
    if avg_protein < (current_user.daily_protein_target or 50) * 0.7:
        insights.append({"type": "info", "message": "Protein intake is consistently low this week", "icon": "💪"})
    if avg_calories > calorie_target * 1.1:
        insights.append({"type": "warning", "message": "Average calories above target this week", "icon": "⚠️"})
    if avg_calories < calorie_target * 0.8:
        insights.append({"type": "info", "message": "You're eating below your calorie target", "icon": "📉"})

    # Mood correlation
    stress_logs = [l for l in logs if l.mood in ["stressed", "anxious", "sad"]]
    if len(stress_logs) > 3:
        insights.append({"type": "behavioral", "message": "You tend to eat more when stressed — try mindful eating", "icon": "🧘"})

    return {
        "period": "last_7_days",
        "averages": {
            "calories": round(avg_calories, 1),
            "protein": round(avg_protein, 1),
            "carbs": round(avg_carbs, 1),
            "fat": round(avg_fat, 1),
            "sugar": round(avg_sugar, 1),
        },
        "targets": {
            "calories": calorie_target,
            "protein": current_user.daily_protein_target or 50,
        },
        "insights": insights,
        "total_logs": len(logs),
    }


@router.get("/predict/weight")
async def predict_weight(
    days_ahead: int = Query(30, ge=7, le=90),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Predict future weight based on current eating patterns."""
    # Get weight history
    weight_result = await db.execute(
        select(WeightLog).where(WeightLog.user_id == current_user.id)
        .order_by(WeightLog.logged_at).limit(30)
    )
    weight_logs = weight_result.scalars().all()

    # Get recent calorie data
    since = datetime.now() - timedelta(days=14)
    food_result = await db.execute(
        select(FoodLog).where(
            and_(FoodLog.user_id == current_user.id, FoodLog.logged_at >= since)
        )
    )
    food_logs = food_result.scalars().all()

    prediction = predictor.predict_weight(
        current_weight=current_user.weight_kg or 70,
        target_weight=current_user.target_weight_kg,
        calorie_target=current_user.daily_calorie_target or 2000,
        food_logs=food_logs,
        weight_history=weight_logs,
        days_ahead=days_ahead,
    )
    return prediction


@router.get("/predict/habits")
async def predict_habit_risks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Detect risky eating patterns."""
    since = datetime.now() - timedelta(days=14)
    result = await db.execute(
        select(FoodLog).where(
            and_(FoodLog.user_id == current_user.id, FoodLog.logged_at >= since)
        ).order_by(FoodLog.logged_at)
    )
    logs = result.scalars().all()

    risks = predictor.detect_habit_risks(logs)
    return {"risks": risks, "analyzed_days": 14}


@router.get("/context-suggestions")
async def get_context_suggestions(
    lat: float = Query(None),
    lon: float = Query(None),
    current_user: User = Depends(get_current_user),
):
    """Context-aware suggestions based on time, weather, location."""
    from services.context_service import ContextEngine
    engine = ContextEngine()
    suggestions = await engine.get_suggestions(current_user, lat, lon)
    return suggestions


@router.get("/digital-twin")
async def get_digital_twin(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Virtual health model simulation."""
    food_result = await db.execute(
        select(FoodLog).where(FoodLog.user_id == current_user.id)
        .order_by(FoodLog.logged_at.desc()).limit(100)
    )
    logs = food_result.scalars().all()

    simulation = predictor.simulate_digital_twin(current_user, logs)
    return simulation
