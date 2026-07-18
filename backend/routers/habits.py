from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import date, datetime
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from database import get_db
from models.user import User
from models.habits import Habit, HabitLog, Achievement
from services.auth_service import get_current_user

router = APIRouter()

SYSTEM_HABITS = [
    {"title": "No Sugar Day", "description": "Avoid added sugar for the entire day", "habit_type": "no_sugar", "target_value": 0, "target_unit": "g sugar", "points_reward": 20},
    {"title": "Drink 3L Water", "description": "Stay hydrated with 3 liters of water", "habit_type": "water_goal", "target_value": 3000, "target_unit": "ml", "points_reward": 15},
    {"title": "No Junk Food", "description": "Avoid processed and junk food", "habit_type": "no_junk", "target_value": 0, "target_unit": "items", "points_reward": 25},
    {"title": "Eat 5 Veggies", "description": "Include 5 different vegetables today", "habit_type": "veggie_goal", "target_value": 5, "target_unit": "servings", "points_reward": 20},
    {"title": "Protein Goal", "description": "Hit your daily protein target", "habit_type": "protein_goal", "target_value": 1, "target_unit": "ratio", "points_reward": 15},
]


class HabitCreate(BaseModel):
    title: str
    description: Optional[str] = None
    habit_type: str
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    points_reward: int = 10


class HabitLogCreate(BaseModel):
    habit_id: UUID
    completed: bool
    value_achieved: Optional[float] = None
    notes: Optional[str] = None


@router.get("/")
async def get_habits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Habit).where(
            and_(Habit.user_id == current_user.id, Habit.is_active == True)
        )
    )
    habits = result.scalars().all()

    # Get today's logs
    today = date.today()
    log_result = await db.execute(
        select(HabitLog).where(
            and_(HabitLog.user_id == current_user.id, HabitLog.date == today)
        )
    )
    today_logs = {str(l.habit_id): l for l in log_result.scalars().all()}

    return [
        {
            "id": str(h.id),
            "title": h.title,
            "description": h.description,
            "habit_type": h.habit_type,
            "target_value": h.target_value,
            "target_unit": h.target_unit,
            "points_reward": h.points_reward,
            "is_system": h.is_system,
            "completed_today": today_logs.get(str(h.id), {}).completed if str(h.id) in today_logs else False,
        }
        for h in habits
    ]


@router.post("/", status_code=201)
async def create_habit(
    data: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    habit = Habit(user_id=current_user.id, **data.model_dump())
    db.add(habit)
    await db.flush()
    return {"id": str(habit.id), "title": habit.title}


@router.post("/seed-system-habits", status_code=201)
async def seed_system_habits(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add pre-built system habits for the user."""
    created = []
    for h_data in SYSTEM_HABITS:
        habit = Habit(user_id=current_user.id, is_system=True, **h_data)
        db.add(habit)
        created.append(h_data["title"])
    return {"created": created}


@router.post("/log", status_code=201)
async def log_habit(
    data: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()

    # Check if already logged today
    existing = await db.execute(
        select(HabitLog).where(
            and_(
                HabitLog.habit_id == data.habit_id,
                HabitLog.user_id == current_user.id,
                HabitLog.date == today,
            )
        )
    )
    log = existing.scalar_one_or_none()

    if log:
        log.completed = data.completed
        log.value_achieved = data.value_achieved
    else:
        log = HabitLog(
            habit_id=data.habit_id,
            user_id=current_user.id,
            date=today,
            completed=data.completed,
            value_achieved=data.value_achieved,
            notes=data.notes,
        )
        db.add(log)

    # Award points if completed
    if data.completed:
        habit_result = await db.execute(select(Habit).where(Habit.id == data.habit_id))
        habit = habit_result.scalar_one_or_none()
        if habit:
            current_user.total_points += habit.points_reward
            db.add(current_user)

    return {"message": "Habit logged", "completed": data.completed}


@router.get("/achievements")
async def get_achievements(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Achievement).where(Achievement.user_id == current_user.id)
        .order_by(Achievement.earned_at.desc())
    )
    achievements = result.scalars().all()
    return [
        {
            "badge_type": a.badge_type,
            "badge_name": a.badge_name,
            "badge_icon": a.badge_icon,
            "points_earned": a.points_earned,
            "earned_at": a.earned_at,
        }
        for a in achievements
    ]


@router.get("/leaderboard")
async def get_leaderboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Top users by points."""
    from models.user import User as UserModel
    result = await db.execute(
        select(UserModel.username, UserModel.total_points, UserModel.current_streak, UserModel.level)
        .order_by(UserModel.total_points.desc())
        .limit(20)
    )
    rows = result.all()
    return [
        {"rank": i + 1, "username": r.username, "points": r.total_points, "streak": r.current_streak, "level": r.level}
        for i, r in enumerate(rows)
    ]
