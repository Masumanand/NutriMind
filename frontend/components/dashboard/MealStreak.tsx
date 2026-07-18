"use client";
import { Flame, Camera, Check } from "lucide-react";
import Link from "next/link";

interface Props {
  streak: {
    current_streak: number;
    breakfast: boolean;
    lunch: boolean;
    dinner: boolean;
    day_complete: boolean;
  };
}

export default function MealStreak({ streak }: Props) {
  const meals = [
    { key: "breakfast", label: "Breakfast", logged: streak.breakfast, time: "Morning" },
    { key: "lunch", label: "Lunch", logged: streak.lunch, time: "Afternoon" },
    { key: "dinner", label: "Dinner", logged: streak.dinner, time: "Evening" },
  ];

  const completedCount = meals.filter((m) => m.logged).length;

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-800 flex items-center gap-2">
          <Flame className="w-4 h-4 text-orange-500" />
          Meal Photo Streak
        </h3>
        <div className="flex items-center gap-1">
          <span className="text-lg font-bold text-orange-500">{streak.current_streak}</span>
          <span className="text-xs text-gray-400">days</span>
        </div>
      </div>

      {/* Progress */}
      <div className="flex items-center gap-2 mb-4">
        <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-orange-400 to-orange-500 rounded-full transition-all duration-500"
            style={{ width: `${(completedCount / 3) * 100}%` }}
          />
        </div>
        <span className="text-xs text-gray-500 font-medium">{completedCount}/3</span>
      </div>

      {/* Meal checklist */}
      <div className="space-y-2">
        {meals.map((meal) => (
          <div key={meal.key} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-5 h-5 rounded-full flex items-center justify-center ${
                meal.logged ? "bg-green-100" : "bg-gray-100"
              }`}>
                {meal.logged ? (
                  <Check className="w-3 h-3 text-green-600" />
                ) : (
                  <Camera className="w-3 h-3 text-gray-400" />
                )}
              </div>
              <span className={`text-sm ${meal.logged ? "text-gray-800" : "text-gray-500"}`}>
                {meal.label}
              </span>
            </div>
            {meal.logged ? (
              <span className="text-[11px] text-green-600 font-medium">Done ✓</span>
            ) : (
              <Link href="/scanner" className="text-[11px] text-brand-600 font-medium hover:text-brand-700">
                Upload →
              </Link>
            )}
          </div>
        ))}
      </div>

      {/* Completion message */}
      {streak.day_complete && (
        <div className="mt-3 p-2 bg-green-50 border border-green-100 rounded-lg text-center">
          <p className="text-xs text-green-700 font-medium">🎉 All meals logged! +50 pts</p>
        </div>
      )}

      {!streak.day_complete && completedCount > 0 && (
        <p className="mt-3 text-[11px] text-gray-400 text-center">
          Upload {3 - completedCount} more meal photo{3 - completedCount > 1 ? "s" : ""} to keep your streak!
        </p>
      )}
    </div>
  );
}
