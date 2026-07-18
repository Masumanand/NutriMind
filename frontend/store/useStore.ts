import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  id: string;
  email: string;
  username: string;
  full_name?: string;
  avatar_url?: string;
  goal?: string;
  diet_type?: string;
  daily_calorie_target?: number;
  total_points: number;
  current_streak: number;
  level: number;
  chatbot_personality: string;
}

interface DailySummary {
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  water_ml: number;
  calorie_target: number;
  water_target_ml: number;
  health_score: number;
  alerts: string[];
  meals: Record<string, unknown[]>;
}

interface AppState {
  // Auth
  user: User | null;
  token: string | null;
  setUser: (user: User) => void;
  setToken: (token: string) => void;
  logout: () => void;

  // Daily data
  dailySummary: DailySummary | null;
  setDailySummary: (summary: DailySummary) => void;

  // UI
  chatOpen: boolean;
  setChatOpen: (open: boolean) => void;
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void; // kept for compatibility

  // Chatbot
  chatMessages: Array<{ role: "user" | "assistant"; content: string; timestamp: Date }>;
  addChatMessage: (msg: { role: "user" | "assistant"; content: string }) => void;
  clearChatMessages: () => void;
}

export const useStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),
      logout: () => {
        set({ user: null, token: null, chatMessages: [] });
      },

      dailySummary: null,
      setDailySummary: (summary) => set({ dailySummary: summary }),

      chatOpen: false,
      setChatOpen: (open) => set({ chatOpen: open }),
      sidebarOpen: true,
      setSidebarOpen: (open) => set({ sidebarOpen: open }),

      chatMessages: [],
      addChatMessage: (msg) =>
        set((state) => ({
          chatMessages: [...state.chatMessages, { ...msg, timestamp: new Date() }],
        })),
      clearChatMessages: () => set({ chatMessages: [] }),
    }),
    {
      name: "nutrimind-store",
      partialize: (state) => ({ user: state.user, token: state.token }),
    }
  )
);
