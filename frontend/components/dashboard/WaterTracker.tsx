"use client";
import { Plus } from "lucide-react";
import toast from "react-hot-toast";
import { foodApi } from "@/lib/api";

interface Props {
  current: number;
  target: number;
}

export default function WaterTracker({ current, target }: Props) {
  const liters = (current / 1000).toFixed(1);
  const targetLiters = (target / 1000).toFixed(1);
  const glasses = Math.floor(current / 250);
  const totalGlasses = Math.ceil(target / 250);
  const filledGlasses = Math.min(glasses, 8);

  const addWater = async () => {
    try {
      await foodApi.logWater(250);
      toast.success("💧 250ml water logged!");
    } catch {
      toast.error("Failed to log water");
    }
  };

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-800">Water Intake</h3>
        <div className="flex items-baseline gap-1">
          <span className="text-lg font-bold text-sky-600">{liters}</span>
          <span className="text-xs text-gray-400">of {targetLiters} Liters</span>
        </div>
      </div>
      <div className="flex items-center gap-1.5 mb-3">
        {Array.from({ length: 8 }).map((_, i) => (
          <div
            key={i}
            className={`w-6 h-8 rounded-md transition-colors ${
              i < filledGlasses ? "bg-sky-400" : "bg-gray-100"
            }`}
          />
        ))}
      </div>
      <button
        onClick={addWater}
        className="flex items-center gap-1.5 text-xs font-medium text-sky-600 hover:text-sky-700 transition-colors"
      >
        <Plus className="w-3.5 h-3.5" /> Add Water
      </button>
    </div>
  );
}
