from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func
import uuid

from database import Base


class FoodItem(Base):
    """Master food database entry."""
    __tablename__ = "food_items"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, index=True)
    brand = Column(String)
    barcode = Column(String, unique=True, index=True)
    category = Column(String)  # fruit, vegetable, grain, protein, dairy, etc.
    cuisine = Column(String)   # Indian, Italian, etc.
    image_url = Column(String)

    # Per 100g values
    calories_per_100g = Column(Float, nullable=False)
    protein_per_100g = Column(Float, default=0)
    carbs_per_100g = Column(Float, default=0)
    fat_per_100g = Column(Float, default=0)
    fiber_per_100g = Column(Float, default=0)
    sugar_per_100g = Column(Float, default=0)
    sodium_per_100g = Column(Float, default=0)
    vitamins = Column(JSON, default=dict)
    minerals = Column(JSON, default=dict)

    # Metadata
    allergens = Column(JSON, default=list)
    diet_tags = Column(JSON, default=list)  # ["vegan", "gluten-free"]
    sustainability_score = Column(Float)    # 0-10 environmental impact
    health_score = Column(Float)            # 0-10 overall health rating
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FoodLog(Base):
    """User's daily food consumption log."""
    __tablename__ = "food_logs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    food_item_id = Column(Uuid(as_uuid=True), ForeignKey("food_items.id"))
    food_name = Column(String, nullable=False)  # fallback if not in DB
    meal_type = Column(String)  # breakfast, lunch, dinner, snack
    quantity_g = Column(Float, nullable=False)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())

    # Computed at log time
    calories = Column(Float)
    protein = Column(Float)
    carbs = Column(Float)
    fat = Column(Float)
    fiber = Column(Float)
    sugar = Column(Float)

    # Context
    mood = Column(String)           # happy, stressed, bored, hungry
    location = Column(String)
    notes = Column(Text)
    logged_via = Column(String, default="manual")  # manual, scanner, voice, chatbot


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    amount_ml = Column(Float, nullable=False)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    weight_kg = Column(Float, nullable=False)
    body_fat_pct = Column(Float)
    muscle_mass_kg = Column(Float)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text)
