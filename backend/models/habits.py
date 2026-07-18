from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, JSON, ForeignKey, Text, Date
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func
import uuid

from database import Base


class Habit(Base):
    __tablename__ = "habits"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    habit_type = Column(String)  # no_sugar, water_goal, no_junk, exercise, etc.
    target_value = Column(Float)
    target_unit = Column(String)  # liters, steps, days
    points_reward = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    is_system = Column(Boolean, default=False)  # pre-built challenges
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class HabitLog(Base):
    __tablename__ = "habit_logs"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    habit_id = Column(Uuid(as_uuid=True), ForeignKey("habits.id"), nullable=False)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)
    completed = Column(Boolean, default=False)
    value_achieved = Column(Float)
    notes = Column(Text)
    logged_at = Column(DateTime(timezone=True), server_default=func.now())


class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    badge_type = Column(String, nullable=False)  # first_log, week_streak, protein_goal, etc.
    badge_name = Column(String, nullable=False)
    badge_icon = Column(String)
    points_earned = Column(Integer, default=0)
    earned_at = Column(DateTime(timezone=True), server_default=func.now())
