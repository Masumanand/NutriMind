from datetime import datetime
from typing import Optional
import httpx

from config import settings
from models.user import User


class ContextEngine:
    """Context-aware suggestion engine based on time, weather, and location."""

    async def get_suggestions(self, user: User, lat: Optional[float], lon: Optional[float]) -> dict:
        now = datetime.now()
        hour = now.hour
        suggestions = []

        # Time-based meal suggestions
        meal_context = self._get_meal_context(hour)
        suggestions.extend(meal_context["suggestions"])

        # Weather-based suggestions
        weather_data = None
        if lat and lon and settings.WEATHER_API_KEY:
            weather_data = await self._get_weather(lat, lon)
            weather_suggestions = self._get_weather_suggestions(weather_data)
            suggestions.extend(weather_suggestions)

        # User-specific context
        if user.medical_conditions:
            if "diabetes" in user.medical_conditions:
                suggestions.append({
                    "type": "medical",
                    "message": "Remember to monitor your blood sugar before and after meals",
                    "icon": "🩺",
                })
            if "hypertension" in user.medical_conditions:
                suggestions.append({
                    "type": "medical",
                    "message": "Keep sodium intake low today — avoid processed foods",
                    "icon": "❤️",
                })

        # Streak motivation
        if user.current_streak > 0:
            suggestions.append({
                "type": "motivation",
                "message": f"🔥 You're on a {user.current_streak}-day streak! Keep it going!",
                "icon": "🔥",
            })

        return {
            "timestamp": now.isoformat(),
            "meal_time": meal_context["meal_type"],
            "weather": weather_data,
            "suggestions": suggestions,
            "greeting": self._get_greeting(hour, user.full_name or user.username),
        }

    def _get_meal_context(self, hour: int) -> dict:
        if 5 <= hour < 10:
            return {
                "meal_type": "breakfast",
                "suggestions": [
                    {"type": "meal_time", "message": "Good morning! Time for a nutritious breakfast 🌅", "icon": "🍳"},
                    {"type": "tip", "message": "A protein-rich breakfast keeps you full until lunch", "icon": "💡"},
                ],
            }
        elif 11 <= hour < 14:
            return {
                "meal_type": "lunch",
                "suggestions": [
                    {"type": "meal_time", "message": "Lunchtime! Aim for a balanced plate 🥗", "icon": "🥗"},
                    {"type": "tip", "message": "Fill half your plate with vegetables for optimal nutrition", "icon": "🥦"},
                ],
            }
        elif 15 <= hour < 17:
            return {
                "meal_type": "snack",
                "suggestions": [
                    {"type": "meal_time", "message": "Afternoon snack time — keep it light and healthy 🍎", "icon": "🍎"},
                    {"type": "tip", "message": "A handful of nuts or fruit is a great energy booster", "icon": "🥜"},
                ],
            }
        elif 18 <= hour < 21:
            return {
                "meal_type": "dinner",
                "suggestions": [
                    {"type": "meal_time", "message": "Dinner time! Keep it lighter than lunch 🌙", "icon": "🍽️"},
                    {"type": "tip", "message": "Avoid heavy carbs late in the evening", "icon": "💡"},
                ],
            }
        else:
            return {
                "meal_type": "rest",
                "suggestions": [
                    {"type": "tip", "message": "Late night? Try herbal tea instead of snacking 🍵", "icon": "🍵"},
                ],
            }

    async def _get_weather(self, lat: float, lon: float) -> Optional[dict]:
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={settings.WEATHER_API_KEY}&units=metric"
            async with httpx.AsyncClient(timeout=5) as http:
                response = await http.get(url)
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "temp_c": data["main"]["temp"],
                        "feels_like": data["main"]["feels_like"],
                        "humidity": data["main"]["humidity"],
                        "condition": data["weather"][0]["main"],
                        "description": data["weather"][0]["description"],
                        "city": data.get("name", ""),
                    }
        except Exception:
            pass
        return None

    def _get_weather_suggestions(self, weather: dict) -> list:
        suggestions = []
        if not weather:
            return suggestions

        temp = weather.get("temp_c", 20)
        condition = weather.get("condition", "")

        if temp > 30:
            suggestions.append({
                "type": "weather",
                "message": f"It's hot today ({temp}°C) — drink extra water and avoid fried foods 💧",
                "icon": "☀️",
            })
        elif temp < 10:
            suggestions.append({
                "type": "weather",
                "message": f"Cold weather ({temp}°C) — warm soups and herbal teas are great today 🍲",
                "icon": "❄️",
            })

        if condition in ["Rain", "Drizzle", "Thunderstorm"]:
            suggestions.append({
                "type": "weather",
                "message": "Rainy day — perfect for a warm, comforting healthy meal at home 🌧️",
                "icon": "🌧️",
            })

        if weather.get("humidity", 50) > 80:
            suggestions.append({
                "type": "weather",
                "message": "High humidity — stay hydrated and opt for light, easy-to-digest foods",
                "icon": "💦",
            })

        return suggestions

    def _get_greeting(self, hour: int, name: str) -> str:
        if hour < 12:
            return f"Good morning, {name}! 🌅"
        elif hour < 17:
            return f"Good afternoon, {name}! ☀️"
        else:
            return f"Good evening, {name}! 🌙"
