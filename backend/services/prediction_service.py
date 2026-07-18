from typing import List, Optional
from datetime import datetime, timedelta
import statistics


class HealthPredictor:
    """
    Predictive health analytics using heuristics and simple time-series modeling.
    Can be upgraded to use scikit-learn or Prophet for production.
    """

    def predict_weight(
        self,
        current_weight: float,
        target_weight: Optional[float],
        calorie_target: int,
        food_logs: list,
        weight_history: list,
        days_ahead: int = 30,
    ) -> dict:
        # Calculate average daily calorie surplus/deficit
        if food_logs:
            daily_calories = {}
            for log in food_logs:
                day = log.logged_at.date()
                daily_calories[day] = daily_calories.get(day, 0) + (log.calories or 0)
            avg_daily_calories = statistics.mean(daily_calories.values()) if daily_calories else calorie_target
        else:
            avg_daily_calories = calorie_target

        # 3500 kcal ≈ 0.45 kg of fat
        daily_surplus = avg_daily_calories - calorie_target
        weight_change_per_day = daily_surplus / 7700  # kg per day

        # Project weight
        projections = []
        projected_weight = current_weight
        for day in range(1, days_ahead + 1):
            projected_weight += weight_change_per_day
            if day % 7 == 0 or day == days_ahead:
                projections.append({
                    "day": day,
                    "date": (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d"),
                    "weight_kg": round(projected_weight, 2),
                })

        # Trend analysis
        if weight_history and len(weight_history) >= 2:
            weights = [w.weight_kg for w in weight_history]
            actual_trend = (weights[-1] - weights[0]) / len(weights)
            trend_direction = "gaining" if actual_trend > 0.05 else "losing" if actual_trend < -0.05 else "stable"
        else:
            trend_direction = "gaining" if daily_surplus > 100 else "losing" if daily_surplus < -100 else "stable"

        # Days to target
        days_to_target = None
        if target_weight and weight_change_per_day != 0:
            diff = target_weight - current_weight
            days_to_target = int(abs(diff / weight_change_per_day))

        message = self._weight_prediction_message(
            current_weight, projected_weight, target_weight, days_ahead, trend_direction
        )

        return {
            "current_weight_kg": current_weight,
            "projected_weight_kg": round(projected_weight, 2),
            "weight_change_kg": round(projected_weight - current_weight, 2),
            "trend": trend_direction,
            "avg_daily_calories": round(avg_daily_calories, 0),
            "daily_surplus_deficit": round(daily_surplus, 0),
            "days_to_target": days_to_target,
            "projections": projections,
            "message": message,
        }

    def detect_habit_risks(self, logs: list) -> list:
        risks = []

        if not logs:
            return [{"type": "no_data", "severity": "info", "message": "Start logging meals to get habit insights"}]

        # Group by day
        daily_logs = {}
        for log in logs:
            day = log.logged_at.date()
            if day not in daily_logs:
                daily_logs[day] = []
            daily_logs[day].append(log)

        # Check for meal skipping
        days_with_logs = len(daily_logs)
        days_skipped = 14 - days_with_logs
        if days_skipped > 5:
            risks.append({
                "type": "meal_skipping",
                "severity": "warning",
                "message": f"You skipped logging meals on {days_skipped} of the last 14 days",
                "recommendation": "Consistent meal logging helps track your nutrition accurately",
            })

        # Check for high sugar pattern
        high_sugar_days = sum(1 for day_logs in daily_logs.values() if sum(l.sugar or 0 for l in day_logs) > 50)
        if high_sugar_days > 5:
            risks.append({
                "type": "high_sugar",
                "severity": "warning",
                "message": f"High sugar intake detected on {high_sugar_days} days",
                "recommendation": "Try replacing sugary snacks with fruits or nuts",
            })

        # Check for late-night eating
        late_night_logs = [l for l in logs if l.logged_at.hour >= 22]
        if len(late_night_logs) > 4:
            risks.append({
                "type": "late_night_eating",
                "severity": "info",
                "message": "Frequent late-night eating detected",
                "recommendation": "Try to finish eating 2-3 hours before bedtime",
            })

        # Stress eating pattern
        stress_logs = [l for l in logs if l.mood in ["stressed", "anxious", "bored"]]
        if len(stress_logs) > 5:
            risks.append({
                "type": "emotional_eating",
                "severity": "behavioral",
                "message": "Pattern of emotional eating detected",
                "recommendation": "Try mindful eating techniques or a short walk when stressed",
            })

        return risks

    def simulate_digital_twin(self, user, logs: list) -> dict:
        """Simulate 30-day health outcomes based on current patterns."""
        if not logs:
            return {"message": "Not enough data for simulation. Log meals for at least 7 days."}

        recent_logs = logs[:50]
        avg_calories = statistics.mean([l.calories or 0 for l in recent_logs]) * 3 if recent_logs else 2000
        avg_protein = statistics.mean([l.protein or 0 for l in recent_logs]) * 3 if recent_logs else 50

        calorie_target = user.daily_calorie_target or 2000
        surplus = avg_calories - calorie_target
        weight_change_30d = round((surplus * 30) / 7700, 2)

        scenarios = {
            "current_path": {
                "label": "If you continue current diet",
                "weight_change_kg": weight_change_30d,
                "projected_weight": round((user.weight_kg or 70) + weight_change_30d, 1),
                "health_trend": "improving" if surplus < 0 else "declining" if surplus > 300 else "stable",
            },
            "optimized_path": {
                "label": "If you hit your calorie target daily",
                "weight_change_kg": 0,
                "projected_weight": user.weight_kg or 70,
                "health_trend": "stable",
            },
            "best_case": {
                "label": "If you follow the full meal plan",
                "weight_change_kg": round(-0.5 * 4, 2),  # ~0.5kg/week loss
                "projected_weight": round((user.weight_kg or 70) - 2.0, 1),
                "health_trend": "significantly improving",
            },
        }

        return {
            "simulation_period_days": 30,
            "current_avg_daily_calories": round(avg_calories, 0),
            "current_avg_protein": round(avg_protein, 1),
            "scenarios": scenarios,
            "key_insight": self._digital_twin_insight(surplus, avg_protein, user),
        }

    def _weight_prediction_message(self, current, projected, target, days, trend) -> str:
        diff = round(projected - current, 1)
        direction = "gain" if diff > 0 else "lose"
        msg = f"Based on your current eating patterns, you'll {direction} {abs(diff)}kg in {days} days."
        if target:
            if (trend == "losing" and projected <= target) or (trend == "gaining" and projected >= target):
                msg += f" You're on track to reach your target weight!"
            else:
                msg += f" Adjust your diet to reach your {target}kg target faster."
        return msg

    def _digital_twin_insight(self, surplus, avg_protein, user) -> str:
        if surplus > 500:
            return "⚠️ Your calorie surplus is high. Reducing portion sizes could significantly improve your health trajectory."
        if avg_protein < (user.daily_protein_target or 50) * 0.7:
            return "💪 Increasing protein intake will help preserve muscle mass and improve satiety."
        if surplus < -300:
            return "📉 You're in a calorie deficit. Great for weight loss, but ensure you're getting enough nutrients."
        return "✅ Your diet is relatively balanced. Small optimizations can make a big difference over time."
