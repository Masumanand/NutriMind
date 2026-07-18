from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from datetime import date, timedelta

from database import get_db
from models.user import User
from models.streak import MealPhotoStreak
from services.auth_service import get_current_user

router = APIRouter()


@router.get("/status")
async def get_streak_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get today's meal photo streak status and overall streak count."""
    today = date.today()

    # Get today's record
    result = await db.execute(
        select(MealPhotoStreak).where(
            and_(
                MealPhotoStreak.user_id == current_user.id,
                MealPhotoStreak.date == today,
            )
        )
    )
    today_record = result.scalar_one_or_none()

    # Calculate current streak (consecutive days with all 3 meals)
    streak_count = 0
    check_date = today - timedelta(days=1)  # start from yesterday

    # If today is already complete, include it
    if today_record and today_record.day_complete:
        streak_count = 1
        # Still check backward from yesterday
    elif today_record:
        # Today is in progress, don't count it yet
        pass

    # Count consecutive past days
    while True:
        result = await db.execute(
            select(MealPhotoStreak).where(
                and_(
                    MealPhotoStreak.user_id == current_user.id,
                    MealPhotoStreak.date == check_date,
                    MealPhotoStreak.day_complete == True,
                )
            )
        )
        day_record = result.scalar_one_or_none()
        if day_record:
            streak_count += 1
            check_date -= timedelta(days=1)
        else:
            break

    # Update user's streak
    if streak_count != current_user.current_streak:
        current_user.current_streak = streak_count
        if streak_count > (current_user.longest_streak or 0):
            current_user.longest_streak = streak_count
        db.add(current_user)

    return {
        "current_streak": streak_count,
        "longest_streak": current_user.longest_streak or 0,
        "today": {
            "breakfast": today_record.breakfast_logged if today_record else False,
            "lunch": today_record.lunch_logged if today_record else False,
            "dinner": today_record.dinner_logged if today_record else False,
            "complete": today_record.day_complete if today_record else False,
        },
    }


@router.post("/log-meal-photo")
async def log_meal_photo(
    meal_type: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Log a healthy meal photo for the streak.
    meal_type: breakfast, lunch, or dinner
    Called automatically when food is logged via scanner/image.
    """
    if meal_type not in ("breakfast", "lunch", "dinner"):
        return {"error": "meal_type must be breakfast, lunch, or dinner"}

    today = date.today()

    # Get or create today's streak record
    result = await db.execute(
        select(MealPhotoStreak).where(
            and_(
                MealPhotoStreak.user_id == current_user.id,
                MealPhotoStreak.date == today,
            )
        )
    )
    record = result.scalar_one_or_none()

    if not record:
        record = MealPhotoStreak(user_id=current_user.id, date=today)
        db.add(record)
        await db.flush()

    # Mark the meal
    if meal_type == "breakfast":
        record.breakfast_logged = True
    elif meal_type == "lunch":
        record.lunch_logged = True
    elif meal_type == "dinner":
        record.dinner_logged = True

    # Check if all three are complete
    was_complete = record.day_complete
    record.day_complete = (
        record.breakfast_logged and record.lunch_logged and record.dinner_logged
    )

    # Award points if day just became complete
    if record.day_complete and not was_complete:
        current_user.total_points += 50  # bonus for completing all 3
        # Recalculate streak
        streak_count = 1
        check_date = today - timedelta(days=1)
        while True:
            prev = await db.execute(
                select(MealPhotoStreak).where(
                    and_(
                        MealPhotoStreak.user_id == current_user.id,
                        MealPhotoStreak.date == check_date,
                        MealPhotoStreak.day_complete == True,
                    )
                )
            )
            if prev.scalar_one_or_none():
                streak_count += 1
                check_date -= timedelta(days=1)
            else:
                break
        current_user.current_streak = streak_count
        if streak_count > (current_user.longest_streak or 0):
            current_user.longest_streak = streak_count
        db.add(current_user)

    db.add(record)

    return {
        "meal_type": meal_type,
        "logged": True,
        "today": {
            "breakfast": record.breakfast_logged,
            "lunch": record.lunch_logged,
            "dinner": record.dinner_logged,
            "complete": record.day_complete,
        },
        "points_awarded": 50 if (record.day_complete and not was_complete) else 0,
    }


@router.get("/history")
async def get_streak_history(
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get streak history for the last N days."""
    since = date.today() - timedelta(days=days)

    result = await db.execute(
        select(MealPhotoStreak).where(
            and_(
                MealPhotoStreak.user_id == current_user.id,
                MealPhotoStreak.date >= since,
            )
        ).order_by(desc(MealPhotoStreak.date))
    )
    records = result.scalars().all()

    return [
        {
            "date": str(r.date),
            "breakfast": r.breakfast_logged,
            "lunch": r.lunch_logged,
            "dinner": r.dinner_logged,
            "complete": r.day_complete,
        }
        for r in records
    ]
