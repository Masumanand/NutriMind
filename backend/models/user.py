from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, Enum, Text
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func
import uuid
import enum

from database import Base


class GoalType(str, enum.Enum):
    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    maintenance = "maintenance"
    general_health = "general_health"


class DietType(str, enum.Enum):
    omnivore = "omnivore"
    vegetarian = "vegetarian"
    vegan = "vegan"
    keto = "keto"
    paleo = "paleo"
    halal = "halal"
    kosher = "kosher"
    gluten_free = "gluten_free"


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    avatar_url = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Health profile
    age = Column(Integer)
    gender = Column(String)
    height_cm = Column(Float)
    weight_kg = Column(Float)
    target_weight_kg = Column(Float)
    activity_level = Column(String, default="moderate")  # sedentary, light, moderate, active, very_active

    # Goals & preferences
    goal = Column(Enum(GoalType), default=GoalType.general_health)
    diet_type = Column(Enum(DietType), default=DietType.omnivore)
    allergies = Column(JSON, default=list)          # ["nuts", "dairy"]
    medical_conditions = Column(JSON, default=list) # ["diabetes", "hypertension"]
    disliked_foods = Column(JSON, default=list)
    budget_weekly = Column(Float)                   # weekly food budget in USD

    # Targets (auto-calculated or user-set)
    daily_calorie_target = Column(Integer)
    daily_protein_target = Column(Float)
    daily_carb_target = Column(Float)
    daily_fat_target = Column(Float)
    daily_water_target = Column(Float, default=2.5)  # liters

    # Gamification
    total_points = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    level = Column(Integer, default=1)

    # Settings
    chatbot_personality = Column(String, default="friendly")  # strict, friendly, scientific
    notifications_enabled = Column(Boolean, default=True)
    location_city = Column(String)
    timezone = Column(String, default="UTC")
