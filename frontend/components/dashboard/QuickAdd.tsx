"use client";
import { Plus, Droplets, Dumbbell, Activity } from "lucide-react";
import Link from "next/link";
import toast from "react-hot-toast";
import { foodApi } from "@/lib/api";

export default function QuickAdd() {
  const logWater = async () => {
    try {
      await foodApi.logWater(250);
      toast.success("💧 250ml water logged!");
    } catch {
      toast.error("Failed to log water");
    }
  };

  const actions = [
    { icon: Plus, label: "Add Meal", href: "/scanner", onClick: undefined },
    { icon: Droplets, label: "Add Water", href: undefined, onClick: logWater },
    { icon: Dumbbell, label: "Log Weight", href: undefined, onClick: () => toast("Coming soon!") },
    { icon: Activity, label: "Add Activity", href: undefined, onClick: () => toast("Coming soon!") },
  ];

  return (
    <div className="glass-card p-5">
      <h3 className="text-sm font-semibold text-gray-800 mb-3">Quick Add</h3>
      <div className="grid grid-cols-4 gap-2">
        {actions.map((action) => {
          const content = (
            <div className="flex flex-col items-center gap-1.5 p-2 rounded-xl hover:bg-gray-50 transition-colors cursor-pointer">
              <div className="w-10 h-10 rounded-full bg-brand-50 flex items-center justify-center">
                <action.icon className="w-4 h-4 text-brand-600" />
              </div>
              <span className="text-[10px] text-gray-500 text-center">{action.label}</span>
            </div>
          );

          if (action.href) {
            return <Link key={action.label} href={action.href}>{content}</Link>;
          }
          return <button key={action.label} onClick={action.onClick}>{content}</button>;
        })}
      </div>
    </div>
  );
}
