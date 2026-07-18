from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from models.user import GoalType, DietType


class UserRegister(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=30)
    password: str = Field(min_length=8)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=10, le=120)
    gender: Optional[str] = None
    height_cm: Optional[float] = Field(None, ge=50, le=300)
    weight_kg: Optional[float] = Field(None, ge=20, le=500)
    target_weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    goal: Optional[GoalType] = None
    diet_type: Optional[DietType] = None
    allergies: Optional[List[str]] = None
    medical_conditions: Optional[List[str]] = None
    disliked_foods: Optional[List[str]] = None
    budget_weekly: Optional[float] = None
    chatbot_personality: Optional[str] = None
    location_city: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    age: Optional[int]
    gender: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    goal: Optional[GoalType]
    diet_type: Optional[DietType]
    daily_calorie_target: Optional[int]
    total_points: int
    current_streak: int
    level: int
    chatbot_personality: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
