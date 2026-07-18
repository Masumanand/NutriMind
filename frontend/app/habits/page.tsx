"use client";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import toast from "react-hot-toast";
import { Flame, Trophy, CheckCircle, Circle, Zap } from "lucide-react";
import { habitsApi } from "@/lib/api";
import AppShell from "@/components/layout/AppShell";

interface Habit { id: string; title: string; description: string; habit_type: string; points_reward: number; is_system: boolean; completed_today: boolean; }
interface LeaderboardEntry { rank: number; username: string; points: number; streak: number; level: number; }
interface Achievement { badge_icon: string; badge_name: string; points_earned: number; earned_at: string; }
type Tab = "habits" | "leaderboard" | "achievements";

export default function HabitsPage() {
  const [tab, setTab] = useState<Tab>("habits");
  const [habits, setHabits] = useState<Habit[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [loading, setLoading] = useState(true);

  const loadHabits = async () => { try { const res = await habitsApi.getHabits(); setHabits(res.data as Habit[]); } catch { toast.error("Failed to load habits"); } };
  const loadLeaderboard = async () => { try { const res = await habitsApi.getLeaderboard(); setLeaderboard(res.data as LeaderboardEntry[]); } catch { toast.error("Failed to load leaderboard"); } };
  const loadAchievements = async () => { try { const res = await habitsApi.getAchievements(); setAchievements(res.data as Achievement[]); } catch { toast.error("Failed to load achievements"); } };

  useEffect(() => { const load = async () => { setLoading(true); await Promise.all([loadHabits(), loadLeaderboard(), loadAchievements()]); setLoading(false); }; load(); }, []);

  const handleToggleHabit = async (habit: Habit) => {
    try { await habitsApi.logHabit({ habit_id: habit.id, completed: !habit.completed_today }); toast.success(habit.completed_today ? "Habit unmarked" : `+${habit.points_reward} points!`); await loadHabits(); } catch { toast.error("Failed to log habit"); }
  };
  const handleSeedHabits = async () => { try { await habitsApi.seedSystemHabits(); toast.success("System habits added!"); await loadHabits(); } catch { toast.error("Failed to seed habits"); } };

  const completedCount = habits.filter((h) => h.completed_today).length;
  const totalCount = habits.length;
  const progressPercent = totalCount > 0 ? (completedCount / totalCount) * 100 : 0;

  if (loading) return <AppShell><div className="flex items-center justify-center h-64"><div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" /></div></AppShell>;

  return (
    <AppShell>
      <div className="space-y-6 animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Flame className="w-7 h-7 text-orange-400" /> Habits & Gamification
          </h1>
          <p className="text-gray-500 text-sm mt-1">Build streaks, earn points, climb the leaderboard</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 p-1 bg-gray-100 rounded-xl w-fit">
          {(["habits", "leaderboard", "achievements"] as Tab[]).map((t) => (
            <button key={t} onClick={() => setTab(t)} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all capitalize ${tab === t ? "bg-white text-brand-600 shadow-sm" : "text-gray-500 hover:text-gray-700"}`}>{t}</button>
          ))}
        </div>

        {tab === "habits" && (
          <div className="space-y-4">
            {totalCount > 0 && (
              <div className="glass-card p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-500">Today&apos;s Progress</span>
                  <span className="text-sm text-gray-800 font-bold">{completedCount}/{totalCount}</span>
                </div>
                <div className="progress-bar"><div className="progress-fill" style={{ width: `${progressPercent}%` }} /></div>
              </div>
            )}
            {habits.length === 0 ? (
              <div className="glass-card p-8 text-center">
                <p className="text-gray-500 mb-4">No habits yet</p>
                <button onClick={handleSeedHabits} className="bg-brand-500 hover:bg-brand-600 text-white font-semibold px-6 py-3 rounded-xl transition-all">
                  <Zap className="w-4 h-4 inline mr-2" />Seed System Habits
                </button>
              </div>
            ) : (
              <div className="space-y-3">
                {habits.map((habit) => (
                  <div key={habit.id} className="glass-card p-4 flex items-center gap-4">
                    <button onClick={() => handleToggleHabit(habit)} className="flex-shrink-0">
                      {habit.completed_today ? <CheckCircle className="w-6 h-6 text-brand-500" /> : <Circle className="w-6 h-6 text-gray-300" />}
                    </button>
                    <div className="flex-1">
                      <h3 className={`font-medium ${habit.completed_today ? "text-gray-400 line-through" : "text-gray-800"}`}>{habit.title}</h3>
                      <p className="text-xs text-gray-400">{habit.description}</p>
                    </div>
                    <div className="flex items-center gap-1 text-yellow-500 text-sm font-bold"><Zap className="w-4 h-4" />{habit.points_reward}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab === "leaderboard" && (
          <div className="space-y-3">
            {leaderboard.map((entry) => (
              <div key={entry.rank} className="glass-card p-4 flex items-center gap-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${entry.rank === 1 ? "bg-yellow-400 text-white" : entry.rank === 2 ? "bg-gray-300 text-white" : entry.rank === 3 ? "bg-orange-400 text-white" : "bg-gray-100 text-gray-500"}`}>{entry.rank}</div>
                <div className="flex-1"><h3 className="text-gray-800 font-medium">{entry.username}</h3><p className="text-xs text-gray-400">Level {entry.level} • {entry.streak} day streak</p></div>
                <div className="flex items-center gap-1 text-yellow-500 font-bold"><Trophy className="w-4 h-4" />{entry.points}</div>
              </div>
            ))}
            {leaderboard.length === 0 && <p className="text-center text-gray-400 py-8">No leaderboard data yet</p>}
          </div>
        )}

        {tab === "achievements" && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {achievements.map((ach, i) => (
              <div key={i} className="glass-card p-5 text-center">
                <div className="text-4xl mb-3">{ach.badge_icon}</div>
                <h3 className="text-gray-800 font-bold text-sm mb-1">{ach.badge_name}</h3>
                <p className="text-yellow-500 text-xs font-bold flex items-center justify-center gap-1"><Zap className="w-3 h-3" /> {ach.points_earned} pts</p>
              </div>
            ))}
            {achievements.length === 0 && <p className="text-center text-gray-400 py-8 col-span-full">No achievements earned yet. Complete habits to earn badges!</p>}
          </div>
        )}
      </div>
    </AppShell>
  );
}
