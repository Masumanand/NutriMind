"use client";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { Zap, Brain, TrendingUp } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { insightsApi } from "@/lib/api";
import AppShell from "@/components/layout/AppShell";

interface Scenario { label: string; weight_change_kg: number; projected_weight: number; health_trend: string; }
interface DigitalTwin { key_insight: string; scenarios: Record<string, Scenario>; }
interface WeightProjection { day: number; weight_kg: number; }
interface WeightPrediction { projections: WeightProjection[]; message: string; }

export default function PredictPage() {
  const [digitalTwin, setDigitalTwin] = useState<DigitalTwin | null>(null);
  const [weightPrediction, setWeightPrediction] = useState<WeightPrediction | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [twinRes, weightRes] = await Promise.allSettled([insightsApi.getDigitalTwin(), insightsApi.predictWeight(60)]);
        if (twinRes.status === "fulfilled") setDigitalTwin(twinRes.value.data as DigitalTwin);
        if (weightRes.status === "fulfilled") setWeightPrediction(weightRes.value.data as WeightPrediction);
      } catch { toast.error("Failed to load predictions"); }
      finally { setLoading(false); }
    };
    load();
  }, []);

  if (loading) return <AppShell><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" /></div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2"><Brain className="w-7 h-7 text-purple-500" /> Predictive Health</h1>
          <p className="text-gray-500 text-sm mt-1">AI-powered predictions and digital twin scenarios</p>
        </div>

        {digitalTwin && digitalTwin.scenarios && (
          <div className="space-y-4">
            <div className="glass-card p-5">
              <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2 mb-2"><Brain className="w-5 h-5 text-purple-500" /> Digital Twin Analysis</h2>
              <p className="text-sm text-gray-500">{digitalTwin.key_insight}</p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {Object.entries(digitalTwin.scenarios).map(([key, scenario]) => (
                <div key={key} className={`p-5 rounded-xl border ${key === "best_case" ? "border-green-200 bg-green-50" : key === "worst_case" ? "border-red-200 bg-red-50" : "border-yellow-200 bg-yellow-50"}`}>
                  <div className="flex items-center gap-2 mb-3">
                    {key === "best_case" ? <Zap className="w-5 h-5 text-green-500" /> : key === "worst_case" ? <TrendingUp className="w-5 h-5 text-red-500" /> : <Brain className="w-5 h-5 text-yellow-500" />}
                    <h3 className="text-gray-800 font-bold text-sm">{scenario.label}</h3>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between"><span className="text-xs text-gray-500">Weight Change</span><span className={`text-sm font-bold ${scenario.weight_change_kg < 0 ? "text-green-600" : scenario.weight_change_kg > 0 ? "text-red-500" : "text-yellow-500"}`}>{scenario.weight_change_kg > 0 ? "+" : ""}{scenario.weight_change_kg} kg</span></div>
                    <div className="flex items-center justify-between"><span className="text-xs text-gray-500">Projected</span><span className="text-sm font-bold text-gray-800">{scenario.projected_weight} kg</span></div>
                    <div className="flex items-center justify-between"><span className="text-xs text-gray-500">Trend</span><span className="text-sm capitalize text-gray-600">{scenario.health_trend}</span></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {weightPrediction && weightPrediction.projections.length > 0 && (
          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2 mb-2"><TrendingUp className="w-5 h-5 text-brand-500" /> 60-Day Weight Projection</h2>
            <p className="text-sm text-gray-500 mb-4">{weightPrediction.message}</p>
            <div className="h-72">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={weightPrediction.projections}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                  <XAxis dataKey="day" stroke="#9ca3af" fontSize={12} />
                  <YAxis stroke="#9ca3af" fontSize={12} domain={["auto", "auto"]} />
                  <Tooltip contentStyle={{ background: "white", border: "1px solid #e5e7eb", borderRadius: "12px" }} formatter={(value: number) => [`${value.toFixed(1)} kg`, "Weight"]} labelFormatter={(label: number) => `Day ${label}`} />
                  <Line type="monotone" dataKey="weight_kg" stroke="#3b8a4a" strokeWidth={2} dot={false} activeDot={{ r: 4, fill: "#3b8a4a" }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}

        {!digitalTwin && !weightPrediction && (
          <div className="glass-card p-8 text-center">
            <Brain className="w-12 h-12 text-purple-200 mx-auto mb-4" />
            <p className="text-gray-500">No prediction data available yet. Log more food to unlock AI predictions.</p>
          </div>
        )}
      </div>
    </AppShell>
  );
}
