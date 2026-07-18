"use client";

const recentMeals = [
  { name: "Oats with Milk", time: "Breakfast · 8:39 AM", calories: 250, emoji: "🥣" },
  { name: "Grilled Chicken Salad", time: "Lunch · 1:15 PM", calories: 450, emoji: "🥗" },
  { name: "Banana", time: "Snack · 4:20 PM", calories: 105, emoji: "🍌" },
  { name: "Vegetable Soup", time: "Dinner · 8:00 PM", calories: 280, emoji: "🍲" },
];

export default function RecentMeals() {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-800">Recent Meals</h3>
        <button className="text-xs text-brand-600 hover:text-brand-700 font-medium">View All</button>
      </div>
      <div className="space-y-3">
        {recentMeals.map((meal) => (
          <div key={meal.name} className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gray-50 flex items-center justify-center text-lg">
              {meal.emoji}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{meal.name}</p>
              <p className="text-[11px] text-gray-400">{meal.time}</p>
            </div>
            <span className="text-sm font-semibold text-gray-700">{meal.calories} kcal</span>
          </div>
        ))}
      </div>
    </div>
  );
}
