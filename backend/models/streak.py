from sqlalchemy import Column, String, Integer, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.types import Uuid
from sqlalchemy.sql import func
import uuid

from database import Base


class MealPhotoStreak(Base):
    """Tracks daily healthy meal photo uploads for breakfast, lunch, dinner."""
    __tablename__ = "meal_photo_streaks"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    date = Column(Date, nullable=False)

    # Each meal photo logged (via scanner/image)
    breakfast_logged = Column(Boolean, default=False)
    lunch_logged = Column(Boolean, default=False)
    dinner_logged = Column(Boolean, default=False)

    # All three = day complete
    day_complete = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
