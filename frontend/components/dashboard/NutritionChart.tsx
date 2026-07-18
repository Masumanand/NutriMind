"use client";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Legend
} from "recharts";
import { format, parseISO } from "date-fns";

interface Props {
  data: Array<{ date: string; calories: number }>;
  target: number;
}

export default function NutritionChart({ data, target }: Props) {
  const formatted = data
    .filter((d) => d.date && !isNaN(parseISO(d.date).getTime()))
    .map((d) => ({
      ...d,
      day: format(parseISO(d.date), "EEE dd"),
      protein: Math.round((d.calories || 0) * 0.25 / 4),
      carbs: Math.round((d.calories || 0) * 0.5 / 4),
      fat: Math.round((d.calories || 0) * 0.25 / 9),
    }));

  if (!formatted.length) {
    return (
      <div className="glass-card p-6 h-full flex items-center justify-center">
        <p className="text-gray-400 text-sm">No data yet — start logging meals to see your trend.</p>
      </div>
    );
  }

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-800">Nutrition Overview (This Week)</h3>
        <select className="text-xs text-gray-500 bg-gray-50 border border-gray-200 rounded-lg px-2 py-1">
          <option>This Week</option>
        </select>
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={formatted} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="day" tick={{ fill: "#9ca3af", fontSize: 11 }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fill: "#9ca3af", fontSize: 11 }} axisLine={false} tickLine={false} />
          <Tooltip
            contentStyle={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "12px", fontSize: "12px" }}
          />
          <Legend iconSize={8} wrapperStyle={{ fontSize: "11px" }} />
          <Line type="monotone" dataKey="calories" stroke="#3b8a4a" strokeWidth={2} dot={{ r: 3 }} name="Calories" />
          <Line type="monotone" dataKey="protein" stroke="#ef4444" strokeWidth={2} dot={{ r: 3 }} name="Protein" />
          <Line type="monotone" dataKey="carbs" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} name="Carbs" />
          <Line type="monotone" dataKey="fat" stroke="#6366f1" strokeWidth={1.5} dot={{ r: 2 }} name="Fat" strokeDasharray="4 4" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
