"""
Seeds demo data ONLY for nutrilife@gmail.com account.
Run: python seed_demo_user.py
"""
import asyncio
import uuid
from datetime import datetime, timedelta, date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select

from database import Base
from config import settings
from models.user import User, GoalType, DietType
from models.food import FoodLog, WaterLog, WeightLog
from models.habits import Habit, HabitLog, Achievement
from services.auth_service import hash_password

DEMO_EMAIL = "nutrilife@gmail.com"
DEMO_USERNAME = "nutrilife"
DEMO_PASSWORD = "nutrilife123"
DEMO_FULL_NAME = "Nutri Life"


async def seed_demo():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        # 1. Find or create the demo user
        result = await session.execute(select(User).where(User.email == DEMO_EMAIL))
        user = result.scalar_one_or_none()

        if not user:
            user = User(
                id=uuid.uuid4(),
                email=DEMO_EMAIL,
                username=DEMO_USERNAME,
                hashed_password=hash_password(DEMO_PASSWORD),
                full_name=DEMO_FULL_NAME,
                age=28,
                gender="female",
                height_cm=165,
                weight_kg=62,
                target_weight_kg=58,
                activity_level="moderate",
                goal=GoalType.weight_loss,
                diet_type=DietType.omnivore,
                allergies=[],
                medical_conditions=[],
                disliked_foods=[],
                daily_calorie_target=1800,
                daily_protein_target=90,
                daily_carb_target=200,
                daily_fat_target=60,
                daily_water_target=2.5,
                total_points=1250,
                current_streak=7,
                longest_streak=14,
                level=5,
                chatbot_personality="friendly",
                location_city="Mumbai",
                timezone="Asia/Kolkata",
            )
            session.add(user)
            await session.flush()
            print(f"✅ Created user: {DEMO_EMAIL}")
        else:
            # Update profile to ensure it has the right data
            user.total_points = 1250
            user.current_streak = 7
            user.longest_streak = 14
            user.level = 5
            user.daily_calorie_target = 1800
            user.daily_protein_target = 90
            user.daily_carb_target = 200
            user.daily_fat_target = 60
            user.daily_water_target = 2.5
            user.weight_kg = 62
            user.target_weight_kg = 58
            user.goal = GoalType.weight_loss
            user.age = 28
            user.gender = "female"
            user.height_cm = 165
            user.activity_level = "moderate"
            print(f"✅ Updated existing user: {DEMO_EMAIL}")

        user_id = user.id

        # 2. Clear old demo data for this user
        from sqlalchemy import delete
        await session.execute(delete(FoodLog).where(FoodLog.user_id == user_id))
        await session.execute(delete(WaterLog).where(WaterLog.user_id == user_id))
        await session.execute(delete(WeightLog).where(WeightLog.user_id == user_id))
        await session.execute(delete(HabitLog).where(HabitLog.user_id == user_id))
        await session.execute(delete(Habit).where(Habit.user_id == user_id))
        await session.execute(delete(Achievement).where(Achievement.user_id == user_id))
        print("🧹 Cleared old demo data")

        # 3. Food logs for the past 7 days
        now = datetime.now()
        meals_per_day = [
            # Day 0 (today)
            [
                {"food_name": "Oatmeal with Berries", "meal_type": "breakfast", "quantity_g": 250, "calories": 320, "protein": 12, "carbs": 52, "fat": 8, "fiber": 6, "sugar": 14, "mood": "happy"},
                {"food_name": "Grilled Chicken Salad", "meal_type": "lunch", "quantity_g": 350, "calories": 420, "protein": 38, "carbs": 18, "fat": 22, "fiber": 5, "sugar": 4, "mood": "happy"},
                {"food_name": "Greek Yogurt with Almonds", "meal_type": "snack", "quantity_g": 150, "calories": 180, "protein": 15, "carbs": 10, "fat": 9, "fiber": 2, "sugar": 6},
            ],
            # Day 1 (yesterday)
            [
                {"food_name": "Eggs & Toast", "meal_type": "breakfast", "quantity_g": 200, "calories": 380, "protein": 22, "carbs": 30, "fat": 18, "fiber": 3, "sugar": 2, "mood": "happy"},
                {"food_name": "Dal Rice with Roti", "meal_type": "lunch", "quantity_g": 400, "calories": 520, "protein": 18, "carbs": 72, "fat": 14, "fiber": 8, "sugar": 3, "mood": "happy"},
                {"food_name": "Paneer Tikka", "meal_type": "dinner", "quantity_g": 250, "calories": 380, "protein": 28, "carbs": 12, "fat": 24, "fiber": 2, "sugar": 3},
                {"food_name": "Banana", "meal_type": "snack", "quantity_g": 120, "calories": 107, "protein": 1.3, "carbs": 27, "fat": 0.4, "fiber": 3, "sugar": 14},
            ],
            # Day 2
            [
                {"food_name": "Smoothie Bowl", "meal_type": "breakfast", "quantity_g": 300, "calories": 290, "protein": 10, "carbs": 48, "fat": 8, "fiber": 7, "sugar": 22, "mood": "happy"},
                {"food_name": "Chicken Biryani", "meal_type": "lunch", "quantity_g": 350, "calories": 550, "protein": 30, "carbs": 65, "fat": 18, "fiber": 3, "sugar": 2, "mood": "stressed"},
                {"food_name": "Vegetable Soup", "meal_type": "dinner", "quantity_g": 300, "calories": 150, "protein": 6, "carbs": 22, "fat": 4, "fiber": 5, "sugar": 6},
                {"food_name": "Mixed Nuts", "meal_type": "snack", "quantity_g": 30, "calories": 175, "protein": 5, "carbs": 6, "fat": 15, "fiber": 2, "sugar": 1},
            ],
            # Day 3
            [
                {"food_name": "Poha", "meal_type": "breakfast", "quantity_g": 200, "calories": 250, "protein": 5, "carbs": 40, "fat": 8, "fiber": 2, "sugar": 3, "mood": "happy"},
                {"food_name": "Grilled Fish with Rice", "meal_type": "lunch", "quantity_g": 350, "calories": 480, "protein": 35, "carbs": 50, "fat": 14, "fiber": 2, "sugar": 1},
                {"food_name": "Chapati with Sabzi", "meal_type": "dinner", "quantity_g": 300, "calories": 360, "protein": 12, "carbs": 48, "fat": 12, "fiber": 6, "sugar": 4},
                {"food_name": "Apple", "meal_type": "snack", "quantity_g": 150, "calories": 78, "protein": 0.4, "carbs": 21, "fat": 0.2, "fiber": 3.6, "sugar": 15},
            ],
            # Day 4
            [
                {"food_name": "Idli Sambar", "meal_type": "breakfast", "quantity_g": 250, "calories": 210, "protein": 7, "carbs": 38, "fat": 3, "fiber": 4, "sugar": 2, "mood": "tired"},
                {"food_name": "Rajma Chawal", "meal_type": "lunch", "quantity_g": 400, "calories": 490, "protein": 16, "carbs": 70, "fat": 14, "fiber": 10, "sugar": 3},
                {"food_name": "Egg Fried Rice", "meal_type": "dinner", "quantity_g": 350, "calories": 520, "protein": 18, "carbs": 62, "fat": 22, "fiber": 3, "sugar": 2, "mood": "stressed"},
                {"food_name": "Protein Bar", "meal_type": "snack", "quantity_g": 60, "calories": 200, "protein": 20, "carbs": 22, "fat": 7, "fiber": 3, "sugar": 8},
            ],
            # Day 5
            [
                {"food_name": "Avocado Toast", "meal_type": "breakfast", "quantity_g": 200, "calories": 340, "protein": 10, "carbs": 28, "fat": 22, "fiber": 8, "sugar": 2, "mood": "happy"},
                {"food_name": "Chicken Wrap", "meal_type": "lunch", "quantity_g": 300, "calories": 450, "protein": 32, "carbs": 38, "fat": 18, "fiber": 4, "sugar": 3},
                {"food_name": "Palak Paneer with Naan", "meal_type": "dinner", "quantity_g": 350, "calories": 480, "protein": 22, "carbs": 42, "fat": 24, "fiber": 5, "sugar": 4},
            ],
            # Day 6
            [
                {"food_name": "Dosa with Chutney", "meal_type": "breakfast", "quantity_g": 200, "calories": 260, "protein": 6, "carbs": 38, "fat": 10, "fiber": 2, "sugar": 2},
                {"food_name": "Chole Bhature", "meal_type": "lunch", "quantity_g": 350, "calories": 620, "protein": 15, "carbs": 68, "fat": 30, "fiber": 8, "sugar": 4, "mood": "bored"},
                {"food_name": "Grilled Salmon", "meal_type": "dinner", "quantity_g": 200, "calories": 416, "protein": 40, "carbs": 0, "fat": 26, "fiber": 0, "sugar": 0},
                {"food_name": "Dark Chocolate", "meal_type": "snack", "quantity_g": 30, "calories": 170, "protein": 2, "carbs": 13, "fat": 12, "fiber": 3, "sugar": 8},
            ],
        ]

        for day_offset, meals in enumerate(meals_per_day):
            day_time = now - timedelta(days=day_offset)
            for i, meal in enumerate(meals):
                hour = {"breakfast": 8, "lunch": 13, "dinner": 20, "snack": 16}.get(meal["meal_type"], 12)
                logged_at = day_time.replace(hour=hour, minute=i * 10, second=0, microsecond=0)
                log = FoodLog(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    food_name=meal["food_name"],
                    meal_type=meal["meal_type"],
                    quantity_g=meal["quantity_g"],
                    calories=meal["calories"],
                    protein=meal["protein"],
                    carbs=meal["carbs"],
                    fat=meal["fat"],
                    fiber=meal.get("fiber", 0),
                    sugar=meal.get("sugar", 0),
                    mood=meal.get("mood"),
                    logged_via="manual",
                    logged_at=logged_at,
                )
                session.add(log)

        print(f"✅ Added food logs for 7 days")

        # 4. Water logs
        for day_offset in range(7):
            day_time = now - timedelta(days=day_offset)
            # 4-6 water entries per day
            water_amounts = [250, 300, 250, 350, 250, 200]
            for i, amount in enumerate(water_amounts[:4 + (day_offset % 3)]):
                logged_at = day_time.replace(hour=8 + i * 2, minute=30, second=0, microsecond=0)
                session.add(WaterLog(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    amount_ml=amount,
                    logged_at=logged_at,
                ))

        print("✅ Added water logs")

        # 5. Weight history (past 30 days, gradual decline)
        start_weight = 63.5
        for day_offset in range(30, -1, -1):
            logged_at = (now - timedelta(days=day_offset)).replace(hour=7, minute=0, second=0, microsecond=0)
            # Gradual weight loss with realistic fluctuations
            import random
            random.seed(day_offset + 42)  # deterministic for reproducibility
            daily_change = -0.05 + random.uniform(-0.15, 0.1)
            weight = start_weight + daily_change * (30 - day_offset)
            weight = round(max(61.0, min(64.0, weight)), 1)

            # Only log every 2-3 days to be realistic
            if day_offset % 3 == 0 or day_offset == 0:
                session.add(WeightLog(
                    id=uuid.uuid4(),
                    user_id=user_id,
                    weight_kg=weight,
                    logged_at=logged_at,
                ))

        print("✅ Added weight history")

        # 6. Habits
        habits_data = [
            {"title": "Drink 2.5L Water", "description": "Stay hydrated throughout the day", "habit_type": "water_goal", "target_value": 2500, "target_unit": "ml", "points_reward": 15, "is_system": True},
            {"title": "No Sugar After 6PM", "description": "Avoid sugary foods in the evening", "habit_type": "no_sugar", "points_reward": 20, "is_system": True},
            {"title": "10,000 Steps", "description": "Walk at least 10,000 steps daily", "habit_type": "exercise", "target_value": 10000, "target_unit": "steps", "points_reward": 25, "is_system": True},
            {"title": "Eat 5 Fruits/Veggies", "description": "Get your 5-a-day servings", "habit_type": "nutrition", "target_value": 5, "target_unit": "servings", "points_reward": 15, "is_system": True},
            {"title": "Protein Goal", "description": "Hit your daily protein target (90g)", "habit_type": "protein_goal", "target_value": 90, "target_unit": "grams", "points_reward": 20, "is_system": True},
            {"title": "Morning Meditation", "description": "5 minutes of mindfulness", "habit_type": "mindfulness", "target_value": 5, "target_unit": "minutes", "points_reward": 10, "is_system": False},
        ]

        habit_objects = []
        for h in habits_data:
            habit = Habit(id=uuid.uuid4(), user_id=user_id, **h)
            session.add(habit)
            habit_objects.append(habit)

        await session.flush()

        # Habit logs for the past 7 days (realistic completion)
        completions = [
            [True, True, True, True, True, True],    # today - all done
            [True, True, False, True, True, True],   # yesterday
            [True, False, True, True, False, True],  # 2 days ago
            [True, True, True, False, True, False],  # 3 days ago
            [True, True, True, True, True, True],    # 4 days ago - all done
            [True, False, True, True, True, True],   # 5 days ago
            [True, True, False, True, False, False],  # 6 days ago
        ]

        for day_offset, day_completions in enumerate(completions):
            log_date = (now - timedelta(days=day_offset)).date()
            for habit, completed in zip(habit_objects, day_completions):
                session.add(HabitLog(
                    id=uuid.uuid4(),
                    habit_id=habit.id,
                    user_id=user_id,
                    date=log_date,
                    completed=completed,
                    logged_at=datetime.combine(log_date, datetime.min.time().replace(hour=21)),
                ))

        print("✅ Added habits and logs")

        # 7. Achievements
        achievements_data = [
            {"badge_type": "first_log", "badge_name": "First Bite", "badge_icon": "🍽️", "points_earned": 50, "earned_at": now - timedelta(days=25)},
            {"badge_type": "week_streak", "badge_name": "7-Day Warrior", "badge_icon": "🔥", "points_earned": 100, "earned_at": now - timedelta(days=18)},
            {"badge_type": "water_champion", "badge_name": "Hydration Hero", "badge_icon": "💧", "points_earned": 75, "earned_at": now - timedelta(days=12)},
            {"badge_type": "protein_goal", "badge_name": "Protein Pro", "badge_icon": "💪", "points_earned": 80, "earned_at": now - timedelta(days=8)},
            {"badge_type": "scanner_10", "badge_name": "Eagle Eye", "badge_icon": "📸", "points_earned": 60, "earned_at": now - timedelta(days=5)},
            {"badge_type": "community_first", "badge_name": "Social Butterfly", "badge_icon": "🦋", "points_earned": 40, "earned_at": now - timedelta(days=3)},
            {"badge_type": "two_week_streak", "badge_name": "Consistency King", "badge_icon": "👑", "points_earned": 200, "earned_at": now - timedelta(days=1)},
        ]

        for ach in achievements_data:
            session.add(Achievement(id=uuid.uuid4(), user_id=user_id, **ach))

        print("✅ Added achievements")

        await session.commit()
        print(f"\n🎉 Demo data seeded for {DEMO_EMAIL}")
        print(f"   Password: {DEMO_PASSWORD}")
        print(f"   Points: 1250 | Streak: 7 days | Level: 5")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_demo())
