from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Form
from pydantic import BaseModel
from typing import Optional
import base64

from models.user import User
from services.auth_service import get_current_user
from services.scanner_service import FoodScanner

router = APIRouter()
scanner = FoodScanner()


class ScanResult(BaseModel):
    food_name: str
    confidence: float
    calories_estimated: float
    protein_g: float
    carbs_g: float
    fat_g: float
    serving_size_g: float
    health_score: float
    sustainability_score: float
    allergens: list[str]
    diet_tags: list[str]
    explanation: str  # Explainable AI: why these values


class BarcodeResult(BaseModel):
    barcode: str
    food_name: str
    brand: str
    health_rating: str  # A, B, C, D, E (Nutri-Score style)
    health_score: float
    calories_per_100g: float
    protein_per_100g: float
    carbs_per_100g: float
    fat_per_100g: float
    sugar_per_100g: float
    additives: list[str]
    recommendation: str


@router.post("/image", response_model=ScanResult)
async def scan_food_image(
    file: UploadFile = File(...),
    serving_size_g: Optional[float] = Form(None),
    current_user: User = Depends(get_current_user),
):
    if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, WebP images supported")

    if file.size and file.size > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    image_bytes = await file.read()
    result = await scanner.analyze_image(image_bytes, serving_size_g, current_user)
    return result


@router.post("/voice")
async def log_via_voice(
    audio_text: str = Form(...),  # transcribed text from frontend
    current_user: User = Depends(get_current_user),
):
    """Parse voice input like 'I ate 2 rotis and dal' into food logs."""
    result = await scanner.parse_voice_input(audio_text, current_user)
    return result


@router.get("/barcode/{barcode}", response_model=BarcodeResult)
async def scan_barcode(
    barcode: str,
    current_user: User = Depends(get_current_user),
):
    result = await scanner.lookup_barcode(barcode)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result
