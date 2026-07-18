"use client";
import { Flame, Beef, Wheat, Droplets, Moon } from "lucide-react";

interface Props {
  today: Record<string, number>;
  targets: Record<string, number>;
}

export default function NutritionStats({ today, targets }: Props) {
  const stats = [
    {
      icon: Flame,
      label: "Calories",
      value: Math.round(today.calories || 0),
      target: targets.calories || 2200,
      unit: "kcal",
      color: "text-orange-500",
      bgColor: "bg-orange-50",
      barColor: "bg-orange-400",
    },
    {
      icon: Beef,
      label: "Protein",
      value: Math.round(today.protein || 0),
      target: targets.protein || 120,
      unit: "g",
      color: "text-blue-500",
      bgColor: "bg-blue-50",
      barColor: "bg-blue-400",
    },
    {
      icon: Wheat,
      label: "Carbs",
      value: Math.round(today.carbs || 0),
      target: targets.carbs || 275,
      unit: "g",
      color: "text-purple-500",
      bgColor: "bg-purple-50",
      barColor: "bg-purple-400",
    },
    {
      icon: Droplets,
      label: "Water",
      value: Number(((today.water_ml || 0) / 1000).toFixed(1)),
      target: Number(((targets.water_ml || 3000) / 1000).toFixed(1)),
      unit: "L",
      color: "text-sky-500",
      bgColor: "bg-sky-50",
      barColor: "bg-sky-400",
    },
    {
      icon: Moon,
      label: "Sleep",
      value: 7.5,
      target: 8,
      unit: "hrs",
      color: "text-indigo-500",
      bgColor: "bg-indigo-50",
      barColor: "bg-indigo-400",
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
      {stats.map((stat) => {
        const pct = Math.min(100, Math.round((stat.value / stat.target) * 100));
        return (
          <div key={stat.label} className="glass-card p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-8 h-8 rounded-lg ${stat.bgColor} flex items-center justify-center`}>
                <stat.icon className={`w-4 h-4 ${stat.color}`} />
              </div>
              <span className="text-xs text-gray-500">{stat.label}</span>
            </div>
            <div className="flex items-baseline gap-1">
              <span className="text-2xl font-bold text-gray-900">{stat.value}</span>
              <span className="text-xs text-gray-400">{stat.unit}</span>
            </div>
            <p className="text-[11px] text-gray-400 mt-0.5">/ {stat.target} {stat.unit}</p>
            <div className="mt-2 h-1.5 bg-gray-100 rounded-full overflow-hidden">
              <div className={`h-full rounded-full ${stat.barColor} transition-all duration-700`} style={{ width: `${pct}%` }} />
            </div>
            <p className="text-[11px] text-gray-400 mt-1">{pct}%</p>
          </div>
        );
      })}
    </div>
  );
}
