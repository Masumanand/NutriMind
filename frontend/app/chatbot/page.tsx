"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Send, Loader2, Settings, Trash2 } from "lucide-react";
import { chatApi, authApi } from "@/lib/api";
import { useStore } from "@/store/useStore";
import toast from "react-hot-toast";
import AppShell from "@/components/layout/AppShell";

const PERSONALITIES = [
  { value: "friendly", label: "Friendly Buddy", emoji: "😊", desc: "Warm, encouraging, fun" },
  { value: "strict", label: "Strict Coach", emoji: "😤", desc: "Direct, firm, accountable" },
  { value: "scientific", label: "Scientific Expert", emoji: "🧪", desc: "Evidence-based, precise" },
];
const MOODS = ["😊 Happy", "😰 Stressed", "😑 Bored", "🤤 Hungry", "😴 Tired"];

export default function ChatbotPage() {
  const { user, setUser, chatMessages, addChatMessage, clearChatMessages } = useStore();
  const [input, setInput] = useState("");
  const [mood, setMood] = useState("");
  const [loading, setLoading] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [chatMessages, loading]);

  const sendMessage = async (text?: string) => {
    const msg = text || input.trim();
    if (!msg || loading) return;
    setInput("");
    addChatMessage({ role: "user", content: msg });
    setLoading(true);
    try {
      const { data } = await chatApi.sendMessage({ message: msg, mood: mood ? mood.split(" ")[1].toLowerCase() : undefined });
      addChatMessage({ role: "assistant", content: data.reply });
    } catch { addChatMessage({ role: "assistant", content: "Connection error. Please try again." }); }
    finally { setLoading(false); }
  };

  const changePersonality = async (p: string) => {
    try {
      await authApi.updateProfile({ chatbot_personality: p });
      if (user) setUser({ ...user, chatbot_personality: p });
      toast.success("Personality updated!");
      setShowSettings(false);
    } catch { toast.error("Failed to update"); }
  };

  const clearHistory = async () => { await chatApi.clearHistory(); clearChatMessages(); toast.success("Chat cleared"); };
  const currentPersonality = PERSONALITIES.find((p) => p.value === (user?.chatbot_personality || "friendly")) || PERSONALITIES[0];

  return (
    <AppShell>
      <div className="flex flex-col h-[calc(100vh-120px)] max-w-3xl mx-auto animate-fade-in">
        <div className="glass-card p-4 mb-4 flex items-center gap-3">
          <div className="w-12 h-12 rounded-full bg-brand-100 flex items-center justify-center text-2xl">{currentPersonality.emoji}</div>
          <div className="flex-1"><h1 className="font-bold text-gray-800">{currentPersonality.label}</h1><p className="text-xs text-gray-500">{currentPersonality.desc} · AI Nutrition Coach</p></div>
          <div className="flex gap-2">
            <button onClick={() => setShowSettings(!showSettings)} className="p-2 rounded-xl text-gray-400 hover:text-gray-600 hover:bg-gray-50 transition-all"><Settings className="w-5 h-5" /></button>
            <button onClick={clearHistory} className="p-2 rounded-xl text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all"><Trash2 className="w-5 h-5" /></button>
          </div>
        </div>

        <AnimatePresence>
          {showSettings && (
            <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="glass-card p-4 mb-4 overflow-hidden">
              <p className="text-sm text-gray-500 mb-3">Choose your coach personality:</p>
              <div className="grid grid-cols-3 gap-2">
                {PERSONALITIES.map((p) => (
                  <button key={p.value} onClick={() => changePersonality(p.value)} className={`p-3 rounded-xl border text-center transition-all ${user?.chatbot_personality === p.value ? "border-brand-500 bg-brand-50" : "border-gray-200 hover:border-brand-300"}`}>
                    <div className="text-2xl mb-1">{p.emoji}</div><p className="text-xs font-medium text-gray-800">{p.label}</p><p className="text-xs text-gray-400 mt-0.5">{p.desc}</p>
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="flex-1 overflow-y-auto space-y-4 mb-4 pr-1">
          {chatMessages.length === 0 && (
            <div className="text-center py-16">
              <div className="text-5xl mb-4">{currentPersonality.emoji}</div>
              <h2 className="text-xl font-bold text-gray-800 mb-2">Hi! I&apos;m your {currentPersonality.label}</h2>
              <p className="text-gray-500 mb-6">Ask me anything about nutrition, food, or health</p>
              <div className="grid grid-cols-2 gap-2 max-w-md mx-auto">
                {["What should I eat for breakfast?", "How do I lose weight healthily?", "Give me a high-protein meal plan", "What foods help with energy?"].map((q) => (
                  <button key={q} onClick={() => sendMessage(q)} className="p-3 text-left text-sm glass-card hover:border-brand-200 text-gray-600 hover:text-brand-600 transition-all">{q}</button>
                ))}
              </div>
            </div>
          )}
          {chatMessages.map((msg, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} gap-3`}>
              {msg.role === "assistant" && <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-sm flex-shrink-0 mt-1">{currentPersonality.emoji}</div>}
              <div className={`max-w-[75%] px-4 py-3 text-sm leading-relaxed ${msg.role === "user" ? "chat-bubble-user" : "chat-bubble-ai"}`}>{msg.content}</div>
            </motion.div>
          ))}
          {loading && <div className="flex justify-start gap-3"><div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-sm flex-shrink-0">{currentPersonality.emoji}</div><div className="chat-bubble-ai px-4 py-3 flex gap-1 items-center"><span className="typing-dot w-2 h-2 rounded-full bg-brand-400" /><span className="typing-dot w-2 h-2 rounded-full bg-brand-400" /><span className="typing-dot w-2 h-2 rounded-full bg-brand-400" /></div></div>}
          <div ref={messagesEndRef} />
        </div>

        <div className="glass-card p-3 space-y-2">
          <div className="flex gap-2 overflow-x-auto pb-1">
            {MOODS.map((m) => (<button key={m} onClick={() => setMood(mood === m ? "" : m)} className={`flex-shrink-0 px-3 py-1 rounded-full text-xs border transition-all ${mood === m ? "border-brand-500 bg-brand-50 text-brand-600" : "border-gray-200 text-gray-400 hover:border-brand-300"}`}>{m}</button>))}
          </div>
          <div className="flex gap-2">
            <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()} placeholder="Ask about food, nutrition, health..." className="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-4 py-2.5 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-brand-300" />
            <button onClick={() => sendMessage()} disabled={!input.trim() || loading} className="p-2.5 rounded-xl bg-brand-500 hover:bg-brand-600 disabled:opacity-40 text-white transition-all">
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
