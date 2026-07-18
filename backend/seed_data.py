"""
Seed script: populates the food database with common items.
Run: python seed_data.py
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models.food import FoodItem
from database import Base
from config import settings

SAMPLE_FOODS = [
    {"name": "Banana", "category": "fruit", "calories_per_100g": 89, "protein_per_100g": 1.1, "carbs_per_100g": 23, "fat_per_100g": 0.3, "fiber_per_100g": 2.6, "sugar_per_100g": 12, "diet_tags": ["vegan", "gluten-free"], "health_score": 8.5, "sustainability_score": 7.0},
    {"name": "Chicken Breast", "category": "protein", "calories_per_100g": 165, "protein_per_100g": 31, "carbs_per_100g": 0, "fat_per_100g": 3.6, "fiber_per_100g": 0, "sugar_per_100g": 0, "diet_tags": ["gluten-free", "halal"], "health_score": 9.0, "sustainability_score": 4.5},
    {"name": "Brown Rice", "category": "grain", "calories_per_100g": 216, "protein_per_100g": 4.5, "carbs_per_100g": 45, "fat_per_100g": 1.8, "fiber_per_100g": 3.5, "sugar_per_100g": 0.7, "diet_tags": ["vegan", "gluten-free"], "health_score": 7.5, "sustainability_score": 7.0},
    {"name": "Broccoli", "category": "vegetable", "calories_per_100g": 34, "protein_per_100g": 2.8, "carbs_per_100g": 7, "fat_per_100g": 0.4, "fiber_per_100g": 2.6, "sugar_per_100g": 1.7, "diet_tags": ["vegan", "gluten-free"], "health_score": 9.5, "sustainability_score": 9.0},
    {"name": "Whole Milk", "category": "dairy", "calories_per_100g": 61, "protein_per_100g": 3.2, "carbs_per_100g": 4.8, "fat_per_100g": 3.3, "fiber_per_100g": 0, "sugar_per_100g": 4.8, "allergens": ["dairy"], "diet_tags": ["vegetarian"], "health_score": 6.5, "sustainability_score": 5.0},
    {"name": "Salmon", "category": "fish", "calories_per_100g": 208, "protein_per_100g": 20, "carbs_per_100g": 0, "fat_per_100g": 13, "fiber_per_100g": 0, "sugar_per_100g": 0, "diet_tags": ["gluten-free"], "health_score": 9.0, "sustainability_score": 5.5},
    {"name": "Avocado", "category": "fruit", "calories_per_100g": 160, "protein_per_100g": 2, "carbs_per_100g": 9, "fat_per_100g": 15, "fiber_per_100g": 7, "sugar_per_100g": 0.7, "diet_tags": ["vegan", "keto", "gluten-free"], "health_score": 9.0, "sustainability_score": 6.0},
    {"name": "Oats", "category": "grain", "calories_per_100g": 389, "protein_per_100g": 17, "carbs_per_100g": 66, "fat_per_100g": 7, "fiber_per_100g": 10, "sugar_per_100g": 1, "diet_tags": ["vegan"], "health_score": 8.5, "sustainability_score": 8.0},
    {"name": "Eggs", "category": "protein", "calories_per_100g": 155, "protein_per_100g": 13, "carbs_per_100g": 1.1, "fat_per_100g": 11, "fiber_per_100g": 0, "sugar_per_100g": 1.1, "allergens": ["eggs"], "diet_tags": ["vegetarian", "keto", "gluten-free"], "health_score": 8.5, "sustainability_score": 6.0},
    {"name": "Lentils", "category": "legume", "calories_per_100g": 116, "protein_per_100g": 9, "carbs_per_100g": 20, "fat_per_100g": 0.4, "fiber_per_100g": 8, "sugar_per_100g": 1.8, "diet_tags": ["vegan", "gluten-free", "halal"], "health_score": 9.0, "sustainability_score": 9.5},
    {"name": "Sweet Potato", "category": "vegetable", "calories_per_100g": 86, "protein_per_100g": 1.6, "carbs_per_100g": 20, "fat_per_100g": 0.1, "fiber_per_100g": 3, "sugar_per_100g": 4.2, "diet_tags": ["vegan", "gluten-free"], "health_score": 9.0, "sustainability_score": 8.5},
    {"name": "Greek Yogurt", "category": "dairy", "calories_per_100g": 59, "protein_per_100g": 10, "carbs_per_100g": 3.6, "fat_per_100g": 0.4, "fiber_per_100g": 0, "sugar_per_100g": 3.2, "allergens": ["dairy"], "diet_tags": ["vegetarian", "gluten-free"], "health_score": 8.5, "sustainability_score": 5.0},
    {"name": "Almonds", "category": "nut", "calories_per_100g": 579, "protein_per_100g": 21, "carbs_per_100g": 22, "fat_per_100g": 50, "fiber_per_100g": 12.5, "sugar_per_100g": 4.4, "allergens": ["nuts"], "diet_tags": ["vegan", "keto", "gluten-free"], "health_score": 8.5, "sustainability_score": 6.5},
    {"name": "Spinach", "category": "vegetable", "calories_per_100g": 23, "protein_per_100g": 2.9, "carbs_per_100g": 3.6, "fat_per_100g": 0.4, "fiber_per_100g": 2.2, "sugar_per_100g": 0.4, "diet_tags": ["vegan", "gluten-free"], "health_score": 9.5, "sustainability_score": 9.0},
    {"name": "Roti (Chapati)", "category": "grain", "cuisine": "Indian", "calories_per_100g": 297, "protein_per_100g": 9, "carbs_per_100g": 55, "fat_per_100g": 5, "fiber_per_100g": 4, "sugar_per_100g": 1, "diet_tags": ["vegetarian", "halal"], "health_score": 7.0, "sustainability_score": 7.5},
    {"name": "Dal (Lentil Soup)", "category": "legume", "cuisine": "Indian", "calories_per_100g": 70, "protein_per_100g": 5, "carbs_per_100g": 10, "fat_per_100g": 1, "fiber_per_100g": 3, "sugar_per_100g": 1, "diet_tags": ["vegan", "gluten-free", "halal"], "health_score": 9.0, "sustainability_score": 9.5},
]


async def seed():
    engine = create_async_engine(settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        for food_data in SAMPLE_FOODS:
            food = FoodItem(**food_data, is_verified=True)
            session.add(food)
        await session.commit()
        print(f"✅ Seeded {len(SAMPLE_FOODS)} food items")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
