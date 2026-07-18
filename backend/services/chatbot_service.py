from typing import AsyncGenerator, Optional
import json
import re

from config import settings
from database import redis_client
from models.user import User

# Only import and init OpenAI if we have a real key
_openai_available = False
_client = None

if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-placeholder"):
    try:
        from openai import AsyncOpenAI
        _client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        _openai_available = True
    except Exception:
        pass


PERSONALITY_PROMPTS = {
    "strict": """You are a strict, no-nonsense nutrition coach. You are direct, firm, and hold users accountable.
You don't sugarcoat things. If someone is eating badly, you tell them clearly but constructively.
Use motivational but firm language. Emojis: 💪😤🎯""",

    "friendly": """You are a warm, encouraging nutrition buddy named Nutri. You're supportive, positive, and fun.
You celebrate small wins, offer gentle nudges, and make healthy eating feel achievable and enjoyable.
Use friendly, conversational language. Emojis: 😊🥗✨🌟""",

    "scientific": """You are a scientific nutrition expert. You provide evidence-based advice with references to
nutritional science. You explain the 'why' behind recommendations using precise terminology while remaining
accessible. Use data and research to back your suggestions. Emojis: 🧪📊🔬""",
}

SYSTEM_BASE = """You are NutriMind AI, an intelligent nutrition and health assistant.

User Profile:
- Name: {name}
- Goal: {goal}
- Diet: {diet_type}
- Allergies: {allergies}
- Medical conditions: {conditions}
- Daily calorie target: {calorie_target} kcal
- Current streak: {streak} days

Personality: {personality_prompt}

Guidelines:
1. Always personalize advice to the user's profile
2. If user mentions stress eating or emotional eating, acknowledge emotions first, then suggest alternatives
3. For food logging requests, extract food name and quantity and return action: "log_food"
4. Keep responses concise (2-4 sentences) unless detailed explanation is requested
5. Always end with an actionable suggestion or question
6. Never give medical diagnoses — recommend consulting a doctor for medical concerns
"""


# ── Built-in nutrition knowledge for offline/no-API mode ──────────────────────

NUTRITION_DB = {
    "cake": {"calories": "250-350 kcal per slice (approx 100g)", "protein": "4-5g", "carbs": "35-45g", "fat": "12-18g", "tip": "Opt for angel food cake (130 cal/slice) if you're watching calories!"},
    "banana": {"calories": "89 kcal per 100g (105 cal for a medium banana)", "protein": "1.1g", "carbs": "23g", "fat": "0.3g", "tip": "Great pre-workout snack — natural sugars + potassium 💪"},
    "rice": {"calories": "130 kcal per 100g (cooked white rice)", "protein": "2.7g", "carbs": "28g", "fat": "0.3g", "tip": "Brown rice has more fiber (3.5g vs 0.4g). Try mixing half-half!"},
    "roti": {"calories": "70-80 kcal per roti (30g)", "protein": "2.5g", "carbs": "15g", "fat": "1g", "tip": "Whole wheat rotis are a good complex carb source."},
    "chicken": {"calories": "165 kcal per 100g (breast, cooked)", "protein": "31g", "carbs": "0g", "fat": "3.6g", "tip": "Grilled > fried. Chicken breast is one of the best lean protein sources."},
    "egg": {"calories": "155 kcal per 100g (78 cal per large egg)", "protein": "13g per 100g (6g per egg)", "carbs": "1.1g", "fat": "11g per 100g", "tip": "Don't skip the yolk — it has most of the vitamins!"},
    "pizza": {"calories": "250-300 kcal per slice", "protein": "10-12g", "carbs": "30-35g", "fat": "10-14g", "tip": "Choose thin crust with veggies to cut calories by 30%."},
    "samosa": {"calories": "260-300 kcal per samosa", "protein": "4g", "carbs": "25g", "fat": "17g", "tip": "Baked samosas have ~40% fewer calories than fried ones."},
    "dal": {"calories": "70-100 kcal per 100g (cooked)", "protein": "5-9g", "carbs": "10-15g", "fat": "1-3g", "tip": "Excellent plant protein! Pair with rice for complete amino acids."},
    "milk": {"calories": "61 kcal per 100ml (whole)", "protein": "3.2g", "carbs": "4.8g", "fat": "3.3g", "tip": "Skim milk: 34 cal/100ml if you want protein without the fat."},
    "paneer": {"calories": "265 kcal per 100g", "protein": "18g", "carbs": "1.2g", "fat": "21g", "tip": "High in protein and calcium. Grill it instead of frying for fewer calories."},
    "biryani": {"calories": "200-250 kcal per 100g", "protein": "8-12g", "carbs": "25-30g", "fat": "8-12g", "tip": "One plate can be 500-700 cal. Control portions and add raita for probiotics."},
    "oats": {"calories": "389 kcal per 100g (dry), ~150 cal per cooked bowl", "protein": "17g per 100g dry", "carbs": "66g", "fat": "7g", "tip": "Top with nuts and berries for a balanced breakfast."},
    "apple": {"calories": "52 kcal per 100g", "protein": "0.3g", "carbs": "14g", "fat": "0.2g", "tip": "Eat with skin for maximum fiber (4.4g). Great snack!"},
    "chocolate": {"calories": "545 kcal per 100g (milk chocolate)", "protein": "8g", "carbs": "60g", "fat": "31g", "tip": "Dark chocolate (70%+) has antioxidants and ~170 cal per 30g serving."},
    "burger": {"calories": "250-350 kcal (basic), 500-800 kcal (fast food)", "protein": "15-25g", "carbs": "25-40g", "fat": "12-40g", "tip": "Homemade with lean meat + whole wheat bun = much healthier."},
    "noodles": {"calories": "138 kcal per 100g (cooked)", "protein": "4.5g", "carbs": "25g", "fat": "2g", "tip": "Instant noodles are high in sodium. Add veggies and an egg for balance."},
    "yogurt": {"calories": "59 kcal per 100g (plain Greek)", "protein": "10g", "carbs": "3.6g", "fat": "0.4g", "tip": "Greek yogurt has 2x the protein of regular. Great for gut health!"},
    "almonds": {"calories": "579 kcal per 100g (161 cal for 23 almonds)", "protein": "21g", "carbs": "22g", "fat": "50g", "tip": "A handful (23 almonds) is a perfect snack — healthy fats + protein."},
    "bread": {"calories": "265 kcal per 100g (white), 247 kcal (whole wheat)", "protein": "9g", "carbs": "49g", "fat": "3.2g", "tip": "Whole grain bread has 2x the fiber and keeps you full longer."},
}

GENERAL_TIPS = {
    "weight loss": [
        "Create a 500 cal deficit for ~0.5kg/week loss. Don't go below 1200 cal/day.",
        "Protein keeps you full longer — aim for 25-30g per meal.",
        "Drink water before meals — it reduces appetite by ~25%.",
    ],
    "muscle gain": [
        "Aim for 1.6-2.2g protein per kg bodyweight.",
        "Eat within 2 hours post-workout for optimal muscle repair.",
        "Caloric surplus of 300-500 cal/day for lean gains.",
    ],
    "snack ideas": [
        "Greek yogurt + berries (150 cal, 15g protein)",
        "Handful of almonds (160 cal, 6g protein)",
        "Apple with peanut butter (200 cal, 7g protein)",
        "Hard boiled eggs (78 cal each, 6g protein)",
        "Hummus with carrot sticks (120 cal, 5g protein)",
    ],
    "high protein": [
        "Chicken breast (31g protein/100g)", "Eggs (6g each)",
        "Greek yogurt (10g/100g)", "Lentils/Dal (9g/100g cooked)",
        "Paneer (18g/100g)", "Fish (20-25g/100g)",
    ],
    "breakfast": [
        "Oats with nuts & banana (~350 cal, 12g protein)",
        "Eggs on toast with avocado (~380 cal, 20g protein)",
        "Greek yogurt parfait with granola (~300 cal, 18g protein)",
        "Poha with peanuts (~250 cal, 8g protein)",
        "Smoothie: banana + protein powder + milk (~320 cal, 25g protein)",
    ],
}


def _find_food_info(message: str) -> Optional[dict]:
    """Search for food items mentioned in the message."""
    msg_lower = message.lower()
    for food, info in NUTRITION_DB.items():
        if food in msg_lower:
            return {"food": food, **info}
    return None


def _get_topic_tips(message: str) -> Optional[list]:
    """Get relevant tips based on keywords in the message."""
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["lose weight", "weight loss", "fat loss", "slim", "diet"]):
        return GENERAL_TIPS["weight loss"]
    if any(w in msg_lower for w in ["muscle", "bulk", "gain weight", "mass"]):
        return GENERAL_TIPS["muscle gain"]
    if any(w in msg_lower for w in ["snack", "between meals", "hungry"]):
        return GENERAL_TIPS["snack ideas"]
    if any(w in msg_lower for w in ["protein", "high protein"]):
        return GENERAL_TIPS["high protein"]
    if any(w in msg_lower for w in ["breakfast", "morning"]):
        return GENERAL_TIPS["breakfast"]
    return None


def _generate_offline_response(user: User, message: str, mood: Optional[str] = None) -> dict:
    """Generate a helpful response using built-in knowledge (no API needed)."""
    name = user.full_name or user.username or "there"
    personality = user.chatbot_personality or "friendly"

    # Check for food calorie questions
    food_info = _find_food_info(message)
    if food_info:
        food = food_info["food"]
        reply = f"🍽️ **{food.title()}** — {food_info['calories']}\n\n"
        reply += f"• Protein: {food_info['protein']}\n• Carbs: {food_info['carbs']}\n• Fat: {food_info['fat']}\n\n"
        reply += f"💡 {food_info['tip']}"
        return {"reply": reply, "suggestions": ["Log this food", f"What's healthier than {food}?", "Show my daily intake"], "action": None, "action_data": None}

    # Check for topic-based tips
    tips = _get_topic_tips(message)
    if tips:
        reply = "Here are some tips:\n\n" + "\n".join(f"• {t}" for t in tips)
        if personality == "strict":
            reply += "\n\n💪 Now stop reading and start doing!"
        elif personality == "friendly":
            reply += f"\n\n✨ You've got this, {name}! Want me to help with a specific meal plan?"
        else:
            reply += "\n\n📊 These recommendations are based on current nutritional research."
        return {"reply": reply, "suggestions": ["Make me a meal plan", "What should I eat now?", "Track my calories"], "action": None, "action_data": None}

    # Check for calorie/nutrition questions
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["how many calories", "calories in", "nutrition in", "nutritional value", "how much protein"]):
        reply = "I don't have that specific food in my database yet. "
        reply += "For accurate info, try using the Food Scanner — just snap a photo or type the food name! 📸"
        return {"reply": reply, "suggestions": ["Open Food Scanner", "Log what I ate", "Show common foods"], "action": None, "action_data": None}

    # Check for greetings
    if any(w in msg_lower for w in ["hi", "hello", "hey", "good morning", "good evening"]):
        if personality == "strict":
            reply = f"Hey {name}. Let's get to work. What did you eat today? 💪"
        elif personality == "scientific":
            reply = f"Hello {name}! Ready to optimize your nutrition today? What can I help you analyze? 🧪"
        else:
            reply = f"Hey {name}! 😊 Great to see you. How can I help with your nutrition today? Want to log a meal, get a snack idea, or check your progress?"
        return {"reply": reply, "suggestions": ["What should I eat?", "How am I doing today?", "Snack ideas"], "action": None, "action_data": None}

    # Check for progress questions
    if any(w in msg_lower for w in ["how am i doing", "my progress", "on track", "status"]):
        target = user.daily_calorie_target or 2000
        streak = user.current_streak or 0
        reply = f"📊 Here's a quick look:\n\n"
        reply += f"• 🔥 Current streak: {streak} days\n"
        reply += f"• 🎯 Daily target: {target} kcal\n"
        reply += f"• ⭐ Level: {user.level or 1}\n\n"
        if streak >= 7:
            reply += "Amazing consistency! Keep this momentum going! 🚀"
        elif streak >= 3:
            reply += "Good progress! A few more days and you'll build a solid habit. 💪"
        else:
            reply += "Let's build that streak! Log your meals consistently and watch the magic happen. ✨"
        return {"reply": reply, "suggestions": ["Show my dashboard", "What should I improve?", "Set a new goal"], "action": None, "action_data": None}

    # Default helpful response
    if personality == "strict":
        reply = f"I'm here to help you eat better, {name}. Ask me about calories in foods, meal ideas, or your progress. No excuses! 😤"
    elif personality == "scientific":
        reply = f"I can help with nutritional analysis, calorie counts, meal planning, and evidence-based dietary advice. What would you like to explore? 🔬"
    else:
        reply = f"I'm your nutrition buddy, {name}! 😊 Here's what I can help with:\n\n• 🍽️ Calories & nutrition info for any food\n• 🥗 Meal suggestions & snack ideas\n• 📊 Track your progress\n• 💡 Diet tips personalized for you\n\nWhat would you like to know?"

    return {"reply": reply, "suggestions": ["Calories in a food", "Healthy snack ideas", "Show my progress"], "action": None, "action_data": None}


class NutriChatbot:
    def __init__(self):
        self.model = settings.OPENAI_MODEL

    def _build_system_prompt(self, user: User) -> str:
        personality = PERSONALITY_PROMPTS.get(user.chatbot_personality or "friendly", PERSONALITY_PROMPTS["friendly"])
        return SYSTEM_BASE.format(
            name=user.full_name or user.username,
            goal=user.goal.value if user.goal else "general health",
            diet_type=user.diet_type.value if user.diet_type else "omnivore",
            allergies=", ".join(user.allergies or []) or "none",
            conditions=", ".join(user.medical_conditions or []) or "none",
            calorie_target=user.daily_calorie_target or 2000,
            streak=user.current_streak,
            personality_prompt=personality,
        )

    async def _get_history(self, user_id: str, limit: int = 10) -> list:
        try:
            key = f"chat_history:{user_id}"
            raw = await redis_client.lrange(key, -limit * 2, -1)
            messages = []
            for item in raw:
                messages.append(json.loads(item))
            return messages
        except Exception:
            return []

    async def _save_message(self, user_id: str, role: str, content: str):
        try:
            key = f"chat_history:{user_id}"
            await redis_client.rpush(key, json.dumps({"role": role, "content": content}))
            await redis_client.ltrim(key, -100, -1)
            await redis_client.expire(key, 86400 * 7)
        except Exception:
            pass  # non-critical — just skip saving if Redis fails

    async def respond(self, user: User, message: str, mood: Optional[str] = None, context: dict = {}) -> dict:
        user_id = str(user.id)

        # If OpenAI is available, use it
        if _openai_available and _client:
            try:
                system_prompt = self._build_system_prompt(user)
                full_message = message
                if mood:
                    full_message = f"[User mood: {mood}] {message}"
                if context:
                    full_message += f"\n[Context: {json.dumps(context)}]"

                history = await self._get_history(user_id)
                messages = [{"role": "system", "content": system_prompt}] + history + [
                    {"role": "user", "content": full_message}
                ]

                response = await _client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500,
                )

                reply_content = response.choices[0].message.content
                await self._save_message(user_id, "user", full_message)
                await self._save_message(user_id, "assistant", reply_content)

                try:
                    parsed = json.loads(reply_content)
                    return {
                        "reply": parsed.get("reply", reply_content),
                        "suggestions": parsed.get("suggestions", []),
                        "action": parsed.get("action"),
                        "action_data": parsed.get("action_data"),
                    }
                except (json.JSONDecodeError, TypeError):
                    return {"reply": reply_content, "suggestions": [], "action": None, "action_data": None}
            except Exception:
                pass  # Fall through to offline mode

        # Offline mode — use built-in knowledge
        result = _generate_offline_response(user, message, mood)
        await self._save_message(user_id, "user", message)
        await self._save_message(user_id, "assistant", result["reply"])
        return result

    async def stream_respond(self, user: User, message: str, mood: Optional[str] = None, context: dict = {}) -> AsyncGenerator[str, None]:
        if _openai_available and _client:
            try:
                system_prompt = self._build_system_prompt(user)
                full_message = message
                if mood:
                    full_message = f"[User mood: {mood}] {message}"

                history = await self._get_history(str(user.id))
                messages = [{"role": "system", "content": system_prompt}] + history + [
                    {"role": "user", "content": full_message}
                ]

                stream = await _client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500,
                    stream=True,
                )

                full_reply = ""
                async for chunk in stream:
                    delta = chunk.choices[0].delta.content or ""
                    full_reply += delta
                    yield delta

                await self._save_message(str(user.id), "user", full_message)
                await self._save_message(str(user.id), "assistant", full_reply)
                return
            except Exception:
                pass

        # Fallback: yield entire offline response at once
        result = _generate_offline_response(user, message, mood)
        yield result["reply"]

    async def stream_respond_simple(self, message: str, mood: Optional[str] = None) -> AsyncGenerator[str, None]:
        """Simplified streaming without user context (for WebSocket)."""
        if _openai_available and _client:
            try:
                messages = [
                    {"role": "system", "content": "You are NutriMind AI, a helpful nutrition assistant."},
                    {"role": "user", "content": message},
                ]
                stream = await _client.chat.completions.create(
                    model=self.model, messages=messages, stream=True, max_tokens=300
                )
                async for chunk in stream:
                    yield chunk.choices[0].delta.content or ""
                return
            except Exception:
                pass

        # Offline fallback
        food_info = _find_food_info(message)
        if food_info:
            yield f"{food_info['food'].title()}: {food_info['calories']}. {food_info['tip']}"
        else:
            yield "I'm your nutrition assistant! Ask me about calories in foods, healthy meals, or diet tips. 😊"

    async def get_history(self, user_id: str, limit: int = 50) -> list:
        return await self._get_history(user_id, limit)

    async def clear_history(self, user_id: str):
        try:
            await redis_client.delete(f"chat_history:{user_id}")
        except Exception:
            pass

    def _needs_structured(self, message: str) -> bool:
        keywords = ["log", "ate", "eaten", "had", "suggest", "recommend", "plan"]
        return any(k in message.lower() for k in keywords)
