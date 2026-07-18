"use client";
import { MoreHorizontal } from "lucide-react";

interface Props {
  today: Record<string, number>;
}

const meals = [
  { name: "Breakfast", time: "8:30 AM", calories: 250, color: "bg-green-500", emoji: "🥣" },
  { name: "Lunch", time: "1:15 PM", calories: 450, color: "bg-orange-400", emoji: "🥗" },
  { name: "Snack", time: "4:20 PM", calories: 105, color: "bg-red-400", emoji: "🍌" },
  { name: "Dinner", time: "8:00 PM", calories: 280, color: "bg-purple-400", emoji: "🍲" },
];

export default function TodaysMeals({ today }: Props) {
  const totalCal = Math.round(today.calories || 0);
  const distributed = totalCal > 0;

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-800">Today&apos;s Meals</h3>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {meals.map((meal) => {
          const cal = distributed ? Math.round(totalCal * (meal.calories / 1085)) : meal.calories;
          return (
            <div key={meal.name} className="bg-gray-50 rounded-xl p-4 relative group hover:bg-gray-100 transition-colors">
              <button className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                <MoreHorizontal className="w-4 h-4 text-gray-400" />
              </button>
              <div className={`w-2.5 h-2.5 rounded-full ${meal.color} mb-2`} />
              <p className="text-xs font-medium text-gray-700">{meal.name}</p>
              <p className="text-[11px] text-gray-400">{meal.time}</p>
              <div className="mt-3 text-3xl">{meal.emoji}</div>
              <p className="mt-2 text-sm font-bold text-gray-800">{cal} <span className="text-xs font-normal text-gray-400">kcal</span></p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
