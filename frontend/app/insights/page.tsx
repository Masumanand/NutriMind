"use client";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { BarChart3, TrendingUp, AlertTriangle, Brain, Activity } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { insightsApi } from "@/lib/api";
import AppShell from "@/components/layout/AppShell";

interface WeeklyInsight { type: string; message: string; icon: string; }
interface WeeklyData { insights: WeeklyInsight[]; averages: Record<string, number>; targets: Record<string, number>; }
interface WeightProjection { day: number; date: string; weight_kg: number; }
interface WeightPrediction { projections: WeightProjection[]; message: string; current_weight_kg: number; projected_weight_kg: number; weight_change_kg: number; trend: string; }
interface HabitRisk { type: string; severity: string; message: string; recommendation: string; }
interface Scenario { label: string; weight_change_kg: number; projected_weight: number; health_trend: string; }
interface DigitalTwin { key_insight: string; scenarios: Record<string, Scenario>; }

export default function InsightsPage() {
  const [weeklyData, setWeeklyData] = useState<WeeklyData | null>(null);
  const [weightPrediction, setWeightPrediction] = useState<WeightPrediction | null>(null);
  const [habitRisks, setHabitRisks] = useState<HabitRisk[]>([]);
  const [digitalTwin, setDigitalTwin] = useState<DigitalTwin | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [weeklyRes, weightRes, habitsRes, twinRes] = await Promise.allSettled([
          insightsApi.getWeeklySummary(), insightsApi.predictWeight(30),
          insightsApi.predictHabits(), insightsApi.getDigitalTwin(),
        ]);
        if (weeklyRes.status === "fulfilled") setWeeklyData(weeklyRes.value.data as WeeklyData);
        if (weightRes.status === "fulfilled") setWeightPrediction(weightRes.value.data as WeightPrediction);
        if (habitsRes.status === "fulfilled") { const d = habitsRes.value.data; setHabitRisks(Array.isArray(d) ? d as HabitRisk[] : (d as { risks?: HabitRisk[] }).risks || []); }
        if (twinRes.status === "fulfilled") setDigitalTwin(twinRes.value.data as DigitalTwin);
      } catch { toast.error("Failed to load insights"); }
      finally { setLoading(false); }
    };
    load();
  }, []);

  if (loading) return <AppShell><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" /></div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2"><BarChart3 className="w-7 h-7 text-brand-500" /> Health Insights</h1>
          <p className="text-gray-500 text-sm mt-1">AI-powered analysis of your nutrition and health patterns</p>
        </div>

        {weeklyData && weeklyData.insights.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-800">Weekly Insights</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {weeklyData.insights.map((insight, i) => (
                <div key={i} className="glass-card p-4 flex items-start gap-3">
                  <div className="w-8 h-8 rounded-lg bg-brand-50 flex items-center justify-center"><TrendingUp className="w-4 h-4 text-brand-500" /></div>
                  <p className="text-sm text-gray-600">{insight.message}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {weeklyData && weeklyData.averages && (
          <div>
            <h2 className="text-lg font-semibold text-gray-800 mb-3">Weekly Averages</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {(["calories", "protein", "carbs", "sugar"] as const).map((key) => (
                <div key={key} className="glass-card p-4 text-center">
                  <p className="text-xs text-gray-500 capitalize mb-1">{key}</p>
                  <p className="text-xl font-bold text-gray-800">{Math.round(weeklyData.averages[key] || 0)}</p>
                  {weeklyData.targets[key] && <p className="text-xs text-gray-400 mt-1">Target: {weeklyData.targets[key]}</p>}
                </div>
              ))}
            </div>
          </div>
        )}

        {weightPrediction && weightPrediction.projections.length > 0 && (
          <div className="glass-card p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2"><TrendingUp className="w-5 h-5 text-brand-500" /> Weight Projection</h2>
              <span className={`text-sm font-medium px-2 py-1 rounded-lg ${weightPrediction.trend === "losing" ? "bg-green-50 text-green-600" : weightPrediction.trend === "gaining" ? "bg-red-50 text-red-600" : "bg-yellow-50 text-yellow-600"}`}>{weightPrediction.trend}</span>
            </div>
            <p className="text-sm text-gray-500 mb-4">{weightPrediction.message}</p>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={weightPrediction.projections}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="date" stroke="#9ca3af" fontSize={12} tickFormatter={(val: string) => val.slice(5)} />
                  <YAxis stroke="#9ca3af" fontSize={12} domain={["auto", "auto"]} />
                  <Tooltip contentStyle={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "12px" }} />
                  <Line type="monotone" dataKey="weight_kg" stroke="#3b8a4a" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="grid grid-cols-3 gap-4 mt-4">
              <div className="text-center"><p className="text-xs text-gray-500">Current</p><p className="text-lg font-bold text-gray-800">{weightPrediction.current_weight_kg} kg</p></div>
              <div className="text-center"><p className="text-xs text-gray-500">Projected</p><p className="text-lg font-bold text-brand-600">{weightPrediction.projected_weight_kg} kg</p></div>
              <div className="text-center"><p className="text-xs text-gray-500">Change</p><p className={`text-lg font-bold ${weightPrediction.weight_change_kg < 0 ? "text-green-600" : "text-red-500"}`}>{weightPrediction.weight_change_kg > 0 ? "+" : ""}{weightPrediction.weight_change_kg} kg</p></div>
            </div>
          </div>
        )}

        {habitRisks.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2"><AlertTriangle className="w-5 h-5 text-yellow-500" /> Habit Risk Analysis</h2>
            {habitRisks.map((risk, i) => (
              <div key={i} className={`glass-card p-4 border ${risk.severity === "high" ? "border-red-200 bg-red-50/50" : risk.severity === "medium" ? "border-yellow-200 bg-yellow-50/50" : "border-green-200 bg-green-50/50"}`}>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-gray-800 capitalize">{risk.type}</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${risk.severity === "high" ? "bg-red-100 text-red-600" : risk.severity === "medium" ? "bg-yellow-100 text-yellow-600" : "bg-green-100 text-green-600"}`}>{risk.severity}</span>
                </div>
                <p className="text-sm text-gray-600">{risk.message}</p>
                <p className="text-xs text-gray-500 mt-2">💡 {risk.recommendation}</p>
              </div>
            ))}
          </div>
        )}

        {digitalTwin && digitalTwin.scenarios && (
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2 mb-3"><Brain className="w-5 h-5 text-purple-500" /> Digital Twin Simulation</h2>
            <p className="text-sm text-gray-500 mb-4">{digitalTwin.key_insight}</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {Object.entries(digitalTwin.scenarios).map(([key, scenario]) => (
                <div key={key} className={`p-4 rounded-xl border ${key === "best_case" ? "border-green-200 bg-green-50/50" : key === "worst_case" ? "border-red-200 bg-red-50/50" : "border-yellow-200 bg-yellow-50/50"}`}>
                  <h4 className="text-sm font-bold text-gray-800 mb-2">{scenario.label}</h4>
                  <p className="text-xs text-gray-500">Weight: <span className="text-gray-700 font-medium">{scenario.weight_change_kg > 0 ? "+" : ""}{scenario.weight_change_kg} kg</span></p>
                  <p className="text-xs text-gray-500">Projected: <span className="text-gray-700 font-medium">{scenario.projected_weight} kg</span></p>
                  <p className="text-xs text-gray-500 mt-1 capitalize">Trend: {scenario.health_trend}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
