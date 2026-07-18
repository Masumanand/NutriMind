from openai import AsyncOpenAI
import base64
import json
import httpx
from typing import Optional

from config import settings
from models.user import User

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

FOOD_VISION_PROMPT = """Analyze this food image and return a JSON response with:
{
  "food_name": "detected dish name",
  "confidence": 0.0-1.0,
  "serving_size_g": estimated grams in image,
  "calories_estimated": total calories,
  "protein_g": grams of protein,
  "carbs_g": grams of carbohydrates,
  "fat_g": grams of fat,
  "health_score": 0-10 (10 = very healthy),
  "sustainability_score": 0-10 (10 = most sustainable),
  "allergens": ["list", "of", "allergens"],
  "diet_tags": ["vegan", "gluten-free", etc],
  "explanation": "Brief explanation of nutritional values and why this score was given"
}

Be precise with nutritional estimates based on visible portion size."""

VOICE_PARSE_PROMPT = """Parse this voice food log into structured JSON:
Input: "{text}"

Return JSON array of food items:
[
  {{
    "food_name": "name",
    "quantity_g": estimated grams,
    "meal_type": "breakfast|lunch|dinner|snack",
    "quantity_description": "original description like '2 rotis'"
  }}
]

Common Indian food estimates: 1 roti = 40g, 1 cup dal = 200g, 1 cup rice = 180g
Common Western: 1 slice bread = 30g, 1 egg = 50g, 1 cup milk = 240ml"""


class FoodScanner:
    async def analyze_image(self, image_bytes: bytes, serving_size_g: Optional[float], user: User) -> dict:
        """Use GPT-4 Vision to analyze food image."""
        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        prompt = FOOD_VISION_PROMPT
        if user.allergies:
            prompt += f"\n\nUser allergies to flag: {', '.join(user.allergies)}"
        if serving_size_g:
            prompt += f"\n\nUser specified serving size: {serving_size_g}g — adjust estimates accordingly."

        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
                    ],
                }
            ],
            response_format={"type": "json_object"},
            max_tokens=600,
        )

        result = json.loads(response.choices[0].message.content)

        # Scale to serving size if provided
        if serving_size_g and result.get("serving_size_g"):
            scale = serving_size_g / result["serving_size_g"]
            for field in ["calories_estimated", "protein_g", "carbs_g", "fat_g"]:
                result[field] = round(result.get(field, 0) * scale, 1)
            result["serving_size_g"] = serving_size_g

        return result

    async def parse_voice_input(self, text: str, user: User) -> dict:
        """Parse natural language food description into structured logs."""
        prompt = VOICE_PARSE_PROMPT.format(text=text)

        response = await client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=400,
        )

        content = response.choices[0].message.content
        try:
            parsed = json.loads(content)
            items = parsed if isinstance(parsed, list) else parsed.get("items", [])
            return {"parsed_items": items, "original_text": text, "item_count": len(items)}
        except json.JSONDecodeError:
            return {"parsed_items": [], "original_text": text, "item_count": 0, "error": "Could not parse"}

    async def lookup_barcode(self, barcode: str) -> Optional[dict]:
        """Look up product by barcode using Open Food Facts API."""
        url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
        async with httpx.AsyncClient(timeout=10) as http:
            response = await http.get(url)
            if response.status_code != 200:
                return None

            data = response.json()
            if data.get("status") != 1:
                return None

            product = data["product"]
            nutriments = product.get("nutriments", {})

            # Calculate Nutri-Score style rating
            calories = nutriments.get("energy-kcal_100g", 0)
            sugar = nutriments.get("sugars_100g", 0)
            fat = nutriments.get("fat_100g", 0)
            fiber = nutriments.get("fiber_100g", 0)
            protein = nutriments.get("proteins_100g", 0)

            health_score = self._calculate_health_score(calories, sugar, fat, fiber, protein)
            health_rating = self._score_to_rating(health_score)

            return {
                "barcode": barcode,
                "food_name": product.get("product_name", "Unknown"),
                "brand": product.get("brands", "Unknown"),
                "health_rating": health_rating,
                "health_score": health_score,
                "calories_per_100g": calories,
                "protein_per_100g": protein,
                "carbs_per_100g": nutriments.get("carbohydrates_100g", 0),
                "fat_per_100g": fat,
                "sugar_per_100g": sugar,
                "additives": product.get("additives_tags", [])[:5],
                "recommendation": self._get_recommendation(health_rating),
            }

    def _calculate_health_score(self, calories, sugar, fat, fiber, protein) -> float:
        score = 10.0
        if calories > 400: score -= 2
        elif calories > 250: score -= 1
        if sugar > 20: score -= 2
        elif sugar > 10: score -= 1
        if fat > 20: score -= 1.5
        if fiber > 5: score += 1
        if protein > 10: score += 0.5
        return max(0, min(10, round(score, 1)))

    def _score_to_rating(self, score: float) -> str:
        if score >= 8: return "A"
        if score >= 6: return "B"
        if score >= 4: return "C"
        if score >= 2: return "D"
        return "E"

    def _get_recommendation(self, rating: str) -> str:
        recs = {
            "A": "Excellent choice! This is a healthy option.",
            "B": "Good choice. Suitable for regular consumption.",
            "C": "Moderate. Consume in reasonable amounts.",
            "D": "Not ideal. Limit consumption of this product.",
            "E": "Poor nutritional profile. Avoid or consume very rarely.",
        }
        return recs.get(rating, "No recommendation available.")
