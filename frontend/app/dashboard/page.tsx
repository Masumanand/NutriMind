"use client";
import { useEffect, useState } from "react";
import { Droplets, Target, TrendingUp, Zap, AlertCircle, RefreshCw, Plus, Moon, Dumbbell } from "lucide-react";
import { healthApi, insightsApi } from "@/lib/api";
import { useStore } from "@/store/useStore";
import AppShell from "@/components/layout/AppShell";
import NutritionChart from "@/components/dashboard/NutritionChart";
import TodaysMeals from "@/components/dashboard/TodaysMeals";
import GoalProgress from "@/components/dashboard/GoalProgress";
import WaterTracker from "@/components/dashboard/WaterTracker";
import RecentMeals from "@/components/dashboard/RecentMeals";
import QuickAdd from "@/components/dashboard/QuickAdd";
import AiInsight from "@/components/dashboard/AiInsight";
import NutritionStats from "@/components/dashboard/NutritionStats";
import MealStreak from "@/components/dashboard/MealStreak";

export default function DashboardPage() {
  const { user } = useStore();
  const [dashboard, setDashboard] = useState<Record<string, unknown> | null>(null);
  const [context, setContext] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const dashRes = await healthApi.getDashboard();
      setDashboard(dashRes.data);
      try {
        const ctxRes = await insightsApi.getContextSuggestions();
        setContext(ctxRes.data);
      } catch { /* context is optional */ }
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setError(msg || "Could not load dashboard. Make sure the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, []);

  if (loading) {
    return (
      <AppShell>
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
        </div>
      </AppShell>
    );
  }

  if (error || !dashboard) {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center h-64 gap-4">
          <AlertCircle className="w-12 h-12 text-red-400/60" />
          <p className="text-gray-500 text-sm text-center max-w-sm">{error || "No dashboard data available."}</p>
          <button onClick={load} className="flex items-center gap-2 px-4 py-2 bg-brand-50 border border-brand-200 text-brand-600 rounded-xl text-sm hover:bg-brand-100 transition-all">
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      </AppShell>
    );
  }

  const today = (dashboard.today as Record<string, number>) || {};
  const targets = (dashboard.targets as Record<string, number>) || {};
  const weeklyCalories = (dashboard.weekly_calories as Array<{ date: string; calories: number }>) || [];
  const mealStreak = (dashboard.meal_streak as { current_streak: number; breakfast: boolean; lunch: boolean; dinner: boolean; day_complete: boolean }) || {
    current_streak: 0, breakfast: false, lunch: false, dinner: false, day_complete: false,
  };

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Hello, {user?.full_name || user?.username || "there"}! 👋
            </h1>
            <p className="text-gray-500 text-sm mt-0.5">Here&apos;s your nutrition overview for today.</p>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-500 bg-white border border-gray-200 rounded-xl px-3 py-2">
            <span>📅</span>
            <span>{new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
          </div>
        </div>

        {/* Nutrition Stats Row */}
        <NutritionStats today={today} targets={targets} />

        {/* Main Content - 3 column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left/Center Column */}
          <div className="lg:col-span-8 space-y-6">
            {/* Nutrition Chart + AI Insight */}
            <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
              <div className="md:col-span-3">
                <NutritionChart data={weeklyCalories} target={targets.calories || 2000} />
              </div>
              <div className="md:col-span-2">
                <AiInsight context={context} />
              </div>
            </div>

            {/* Today's Meals */}
            <TodaysMeals today={today} />
          </div>

          {/* Right Column */}
          <div className="lg:col-span-4 space-y-6">
            <GoalProgress today={today} targets={targets} />
            <MealStreak streak={mealStreak} />
            <QuickAdd />
            <WaterTracker current={today.water_ml || 0} target={targets.water_ml || 3000} />
            <RecentMeals />
          </div>
        </div>
      </div>
    </AppShell>
  );
}
