"use client";
import { useState } from "react";
import toast from "react-hot-toast";
import { ShoppingCart, Calendar, Loader2, ChevronDown, ChevronUp, Leaf } from "lucide-react";
import { plannerApi } from "@/lib/api";
import AppShell from "@/components/layout/AppShell";

interface MealItem { name: string; calories: number; prep_time_min: number; }
interface MealPlanDay { [mealType: string]: MealItem; }
interface MealPlan { meal_plan: Record<string, MealPlanDay>; nutrition_highlights?: string[]; }
interface GroceryItem { item: string; quantity: string; estimated_cost_usd?: number; }
interface GroceryList { grocery_list: Record<string, GroceryItem[]>; total_estimated_cost_usd?: number; cost_saving_tips?: string[]; }
interface Recommendation { name: string; calories: number; protein_g: number; carbs_g: number; fat_g: number; prep_time_min: number; difficulty: string; why_recommended: string; sustainability_score: number; }
type Tab = "mealplan" | "grocery" | "recs";

export default function PlannerPage() {
  const [tab, setTab] = useState<Tab>("mealplan");
  const [budget, setBudget] = useState("");
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [groceryList, setGroceryList] = useState<GroceryList | null>(null);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedDays, setExpandedDays] = useState<Record<string, boolean>>({});

  const handleGenerateMealPlan = async () => { setLoading(true); try { const params: { days?: number; budget_usd?: number } = { days: 7 }; if (budget) params.budget_usd = parseFloat(budget); const res = await plannerApi.getMealPlan(params); setMealPlan(res.data as MealPlan); toast.success("Meal plan generated!"); } catch { toast.error("Failed to generate meal plan"); } finally { setLoading(false); } };
  const handleGenerateGroceryList = async () => { setLoading(true); try { const params: { budget_usd?: number } = {}; if (budget) params.budget_usd = parseFloat(budget); const res = await plannerApi.getGroceryList(params); setGroceryList(res.data as GroceryList); toast.success("Grocery list ready!"); } catch { toast.error("Failed to generate grocery list"); } finally { setLoading(false); } };
  const handleGetRecommendations = async () => { setLoading(true); try { const res = await plannerApi.getRecommendations(); const data = res.data; if (Array.isArray(data)) setRecommendations(data as Recommendation[]); else setRecommendations((data as { recommendations?: Recommendation[] }).recommendations || []); toast.success("Recommendations loaded!"); } catch { toast.error("Failed to get recommendations"); } finally { setLoading(false); } };

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2"><Calendar className="w-7 h-7 text-brand-500" /> Meal Planner</h1>
          <p className="text-gray-500 text-sm mt-1">AI-generated meal plans, grocery lists, and recommendations</p>
        </div>

        <div className="glass-card p-4 flex items-center gap-4 flex-wrap">
          <label className="text-sm text-gray-500">Budget (USD):</label>
          <input type="number" value={budget} onChange={(e) => setBudget(e.target.value)} placeholder="Optional budget..." className="bg-gray-50 border border-gray-200 rounded-xl text-gray-800 placeholder-gray-400 focus:outline-none focus:border-brand-300 px-4 py-2 w-40 text-sm" />
        </div>

        <div className="flex gap-1 p-1 bg-gray-100 rounded-xl w-fit">
          {([{ key: "mealplan", label: "Meal Plan" }, { key: "grocery", label: "Grocery List" }, { key: "recs", label: "Quick Recs" }] as { key: Tab; label: string }[]).map((t) => (
            <button key={t.key} onClick={() => setTab(t.key)} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${tab === t.key ? "bg-white text-brand-600 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}>{t.label}</button>
          ))}
        </div>

        {tab === "mealplan" && (
          <div className="space-y-4">
            <button onClick={handleGenerateMealPlan} disabled={loading} className="bg-brand-500 hover:bg-brand-600 text-white font-semibold px-6 py-3 rounded-xl transition-all disabled:opacity-50 flex items-center gap-2">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Calendar className="w-4 h-4" />} Generate Meal Plan
            </button>
            {mealPlan && (
              <div className="space-y-3">
                {mealPlan.nutrition_highlights && mealPlan.nutrition_highlights.length > 0 && (
                  <div className="glass-card p-4"><h3 className="text-sm font-medium text-gray-800 mb-2">Nutrition Highlights</h3><ul className="space-y-1">{mealPlan.nutrition_highlights.map((h, i) => <li key={i} className="text-xs text-gray-500 flex items-center gap-2"><Leaf className="w-3 h-3 text-brand-500" /> {h}</li>)}</ul></div>
                )}
                {Object.entries(mealPlan.meal_plan).map(([day, meals]) => (
                  <div key={day} className="glass-card overflow-hidden">
                    <button onClick={() => setExpandedDays((prev) => ({ ...prev, [day]: !prev[day] }))} className="w-full p-4 flex items-center justify-between hover:bg-gray-50 transition-all">
                      <h3 className="text-gray-800 font-medium capitalize">{day}</h3>
                      {expandedDays[day] ? <ChevronUp className="w-4 h-4 text-gray-400" /> : <ChevronDown className="w-4 h-4 text-gray-400" />}
                    </button>
                    {expandedDays[day] && (
                      <div className="px-4 pb-4 space-y-2 border-t border-gray-100 pt-3">
                        {Object.entries(meals).map(([mealType, meal]) => (
                          <div key={mealType} className="flex items-center justify-between">
                            <div><span className="text-xs text-gray-400 capitalize">{mealType}</span><p className="text-sm text-gray-800">{meal.name}</p></div>
                            <div className="text-right"><p className="text-xs text-gray-500">{meal.calories} cal</p><p className="text-xs text-gray-400">{meal.prep_time_min} min</p></div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === "grocery" && (
          <div className="space-y-4">
            <button onClick={handleGenerateGroceryList} disabled={loading} className="bg-brand-500 hover:bg-brand-600 text-white font-semibold px-6 py-3 rounded-xl transition-all disabled:opacity-50 flex items-center gap-2">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ShoppingCart className="w-4 h-4" />} Generate Grocery List
            </button>
            {groceryList && (
              <div className="space-y-4">
                {groceryList.total_estimated_cost_usd && (<div className="glass-card p-4 flex items-center justify-between"><span className="text-sm text-gray-500">Estimated Total</span><span className="text-lg font-bold text-brand-600">${groceryList.total_estimated_cost_usd.toFixed(2)}</span></div>)}
                {Object.entries(groceryList.grocery_list).map(([category, items]) => (
                  <div key={category} className="glass-card p-4"><h3 className="text-gray-800 font-medium capitalize mb-3">{category}</h3><div className="space-y-2">{items.map((item, i) => (<div key={i} className="flex items-center justify-between text-sm"><span className="text-gray-700">{item.item}</span><div className="flex items-center gap-3"><span className="text-gray-400">{item.quantity}</span>{item.estimated_cost_usd !== undefined && <span className="text-brand-600 text-xs">${item.estimated_cost_usd.toFixed(2)}</span>}</div></div>))}</div></div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === "recs" && (
          <div className="space-y-4">
            <button onClick={handleGetRecommendations} disabled={loading} className="bg-brand-500 hover:bg-brand-600 text-white font-semibold px-6 py-3 rounded-xl transition-all disabled:opacity-50 flex items-center gap-2">
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Leaf className="w-4 h-4" />} Get Recommendations
            </button>
            {recommendations.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recommendations.map((rec, i) => (
                  <div key={i} className="glass-card p-5">
                    <div className="flex items-start justify-between mb-3"><h3 className="text-gray-800 font-medium">{rec.name}</h3><div className="flex items-center gap-1"><Leaf className="w-3 h-3 text-brand-500" /><span className="text-xs text-brand-600 font-bold">{rec.sustainability_score}/10</span></div></div>
                    <div className="grid grid-cols-4 gap-2 mb-3">
                      {[{ label: "Cal", val: rec.calories }, { label: "Protein", val: `${rec.protein_g}g` }, { label: "Carbs", val: `${rec.carbs_g}g` }, { label: "Fat", val: `${rec.fat_g}g` }].map((m) => (<div key={m.label} className="text-center"><p className="text-xs text-gray-400">{m.label}</p><p className="text-sm font-bold text-gray-800">{m.val}</p></div>))}
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-400 mb-2"><span>⏱ {rec.prep_time_min} min</span><span className="capitalize">{rec.difficulty}</span></div>
                    <p className="text-xs text-gray-500 italic">{rec.why_recommended}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </AppShell>
  );
}
