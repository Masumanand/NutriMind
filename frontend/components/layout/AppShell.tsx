"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import ChatbotWidget from "@/components/chatbot/ChatbotWidget";
import { useStore } from "@/store/useStore";
import { Search, Bell, ChevronDown } from "lucide-react";

export default function AppShell({ children }: { children: React.ReactNode }) {
  const token = useStore((s) => s.token);
  const user = useStore((s) => s.user);
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (!mounted) return;
    // Read directly from localStorage as fallback
    const storeToken = useStore.getState().token;
    let hasToken = !!storeToken;

    if (!hasToken) {
      // Check localStorage directly in case Zustand hasn't rehydrated
      try {
        const raw = localStorage.getItem("nutrimind-store");
        if (raw) {
          const parsed = JSON.parse(raw);
          hasToken = !!parsed?.state?.token;
        }
      } catch {}
    }

    if (!hasToken) {
      router.replace("/login");
    }
  }, [mounted, token, router]);

  if (!mounted) {
    return (
      <div className="flex min-h-screen bg-surface-primary items-center justify-center">
        <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  // Check token from store OR localStorage
  const storeToken = token;
  let hasValidToken = !!storeToken;
  if (!hasValidToken && typeof window !== "undefined") {
    try {
      const raw = localStorage.getItem("nutrimind-store");
      if (raw) {
        const parsed = JSON.parse(raw);
        hasValidToken = !!parsed?.state?.token;
      }
    } catch {}
  }

  if (!hasValidToken) {
    return (
      <div className="flex min-h-screen bg-surface-primary items-center justify-center">
        <div className="w-8 h-8 border-2 border-brand-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-surface-primary">
      <Sidebar />
      <main className="flex-1 ml-[240px] min-h-screen overflow-y-auto">
        {/* Top Bar */}
        <header className="sticky top-0 z-30 bg-white/80 backdrop-blur-md border-b border-gray-100 px-6 py-3 flex items-center justify-between">
          {/* Search */}
          <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 w-80">
            <Search className="w-4 h-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search foods, recipes, meals..."
              className="bg-transparent text-sm text-gray-700 placeholder-gray-400 outline-none flex-1"
            />
            <kbd className="text-[10px] text-gray-400 bg-white border border-gray-200 rounded px-1.5 py-0.5">⌘K</kbd>
          </div>

          {/* Right side */}
          <div className="flex items-center gap-4">
            <button className="relative p-2 rounded-xl hover:bg-gray-50 transition-colors">
              <Bell className="w-5 h-5 text-gray-500" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
            </button>
            <div className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 rounded-xl px-2 py-1.5 transition-colors">
              <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-xs font-bold text-brand-700">
                {(user?.full_name || user?.username || "U")[0].toUpperCase()}
              </div>
              <span className="text-sm font-medium text-gray-700">{user?.full_name || user?.username}</span>
              <ChevronDown className="w-3.5 h-3.5 text-gray-400" />
            </div>
          </div>
        </header>

        <div className="p-6 max-w-[1400px] mx-auto">
          {children}
        </div>
      </main>
      <ChatbotWidget />
    </div>
  );
}
