"use client";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

interface Props {
  today: Record<string, number>;
  targets: Record<string, number>;
}

export default function GoalProgress({ today, targets }: Props) {
  const calPct = Math.min(100, Math.round(((today.calories || 0) / (targets.calories || 2200)) * 100));
  const protPct = Math.min(100, Math.round(((today.protein || 0) / (targets.protein || 120)) * 100));
  const waterPct = Math.min(100, Math.round(((today.water_ml || 0) / (targets.water_ml || 3000)) * 100));
  const overallPct = Math.round((calPct + protPct + waterPct) / 3);

  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-gray-800">Today&apos;s Goal</h3>
        <button className="text-xs text-brand-600 hover:text-brand-700 font-medium">Edit Goal</button>
      </div>
      <div className="flex items-center gap-4">
        <div className="w-20 h-20">
          <CircularProgressbar
            value={overallPct}
            text={`${overallPct}%`}
            styles={buildStyles({
              textSize: "22px",
              pathColor: "#3b8a4a",
              textColor: "#1a2e1f",
              trailColor: "#e8f5e9",
              strokeLinecap: "round",
            })}
          />
        </div>
        <div>
          <p className="text-sm font-semibold text-gray-800">
            {overallPct >= 70 ? "You're doing great!" : "Keep going!"}
          </p>
          <p className="text-xs text-gray-500 mt-0.5 leading-relaxed">
            Keep it up and achieve your daily nutrition goal.
          </p>
        </div>
      </div>
    </div>
  );
}
