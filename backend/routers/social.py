from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from database import get_mongo
from models.user import User
from services.auth_service import get_current_user

router = APIRouter()


class PostCreate(BaseModel):
    content: str
    image_url: Optional[str] = None
    post_type: str = "progress"  # progress, meal, achievement, challenge


def _require_mongo():
    mongo = get_mongo()
    if mongo is None:
        raise HTTPException(status_code=503, detail="Social features require MongoDB")
    return mongo


@router.get("/feed")
async def get_social_feed(
    current_user: User = Depends(get_current_user),
    limit: int = 20,
    skip: int = 0,
):
    mongo = _require_mongo()
    posts = await mongo.social_posts.find(
        {"is_public": True}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    for post in posts:
        post["_id"] = str(post["_id"])

    total = await mongo.social_posts.count_documents({"is_public": True})
    return {"posts": posts, "total": total}


@router.post("/post", status_code=201)
async def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
):
    mongo = _require_mongo()
    post = {
        "user_id": str(current_user.id),
        "username": current_user.username,
        "avatar_url": current_user.avatar_url,
        "content": data.content,
        "image_url": data.image_url,
        "post_type": data.post_type,
        "likes": 0,
        "comments": [],
        "is_public": True,
        "created_at": datetime.utcnow(),
    }
    result = await mongo.social_posts.insert_one(post)
    return {"id": str(result.inserted_id), "message": "Posted successfully"}


@router.post("/post/{post_id}/like")
async def like_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
):
    mongo = _require_mongo()
    from bson import ObjectId
    await mongo.social_posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$inc": {"likes": 1}}
    )
    return {"message": "Liked"}


@router.get("/challenges")
async def get_community_challenges(current_user: User = Depends(get_current_user)):
    return {
        "challenges": [
            {
                "id": "no_sugar_week",
                "title": "No Sugar Week 🍬",
                "description": "Avoid added sugar for 7 days",
                "participants": 1247,
                "days_left": 3,
                "reward_points": 100,
                "your_status": "active",
            },
            {
                "id": "hydration_challenge",
                "title": "Hydration Hero 💧",
                "description": "Drink 3L water daily for 14 days",
                "participants": 892,
                "days_left": 10,
                "reward_points": 150,
                "your_status": "not_joined",
            },
            {
                "id": "veggie_power",
                "title": "Veggie Power 🥦",
                "description": "Eat 5 servings of vegetables daily for 7 days",
                "participants": 634,
                "days_left": 5,
                "reward_points": 80,
                "your_status": "completed",
            },
        ]
    }
