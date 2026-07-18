"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Smile, Brain, Loader2 } from "lucide-react";
import { useStore } from "@/store/useStore";
import { chatApi } from "@/lib/api";
import toast from "react-hot-toast";

const MOODS = [
  { value: "happy", emoji: "😊" },
  { value: "stressed", emoji: "😰" },
  { value: "bored", emoji: "😑" },
  { value: "hungry", emoji: "🤤" },
  { value: "tired", emoji: "😴" },
];

const QUICK_PROMPTS = [
  "What should I eat for lunch?",
  "How many calories in a banana?",
  "Give me a high-protein snack idea",
  "Am I on track today?",
];

export default function ChatbotWidget() {
  const { chatOpen, setChatOpen, chatMessages, addChatMessage, user } = useStore();
  const [input, setInput] = useState("");
  const [mood, setMood] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [showMoods, setShowMoods] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, loading]);

  const sendMessage = async (text?: string) => {
    const msg = text || input.trim();
    if (!msg || loading) return;
    setInput("");
    addChatMessage({ role: "user", content: msg });
    setLoading(true);
    try {
      const { data } = await chatApi.sendMessage({ message: msg, mood: mood || undefined });
      addChatMessage({ role: "assistant", content: data.reply });
      if (data.action === "log_food" && data.action_data) {
        toast.success("Food detected! Tap to log it 🍽️");
      }
    } catch {
      addChatMessage({ role: "assistant", content: "Sorry, I'm having trouble connecting. Please try again! 🔄" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* FAB */}
      <motion.button
        onClick={() => setChatOpen(!chatOpen)}
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-brand-500 shadow-lg shadow-brand-500/20 flex items-center justify-center"
        aria-label="Open AI Coach"
      >
        <AnimatePresence mode="wait">
          {chatOpen ? (
            <motion.div key="close" initial={{ rotate: -90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: 90, opacity: 0 }}>
              <X className="w-6 h-6 text-white" />
            </motion.div>
          ) : (
            <motion.div key="open" initial={{ rotate: 90, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }} exit={{ rotate: -90, opacity: 0 }}>
              <Brain className="w-6 h-6 text-white" />
            </motion.div>
          )}
        </AnimatePresence>
      </motion.button>

      {/* Chat panel */}
      <AnimatePresence>
        {chatOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-24 right-6 z-50 w-[380px] max-h-[600px] flex flex-col bg-white border border-gray-200 rounded-2xl overflow-hidden shadow-2xl"
          >
            {/* Header */}
            <div className="flex items-center gap-3 p-4 border-b border-gray-100 bg-brand-50">
              <div className="w-10 h-10 rounded-full bg-brand-500 flex items-center justify-center text-lg">
                😊
              </div>
              <div>
                <p className="font-semibold text-gray-800">Nutri AI Coach</p>
                <p className="text-xs text-gray-500">Your AI Nutrition Coach · Online</p>
              </div>
              <div className="ml-auto flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-green-400" />
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-[300px] max-h-[400px] bg-gray-50">
              {chatMessages.length === 0 && (
                <div className="text-center py-8">
                  <div className="text-4xl mb-3">😊</div>
                  <p className="text-gray-600 text-sm">Hi! I&apos;m Nutri, your nutrition coach.</p>
                  <p className="text-gray-400 text-xs mt-1">Ask me anything about food and health!</p>
                  <div className="mt-4 space-y-2">
                    {QUICK_PROMPTS.map((p) => (
                      <button key={p} onClick={() => sendMessage(p)} className="block w-full text-left text-xs px-3 py-2 rounded-lg bg-white border border-gray-200 text-gray-600 hover:text-brand-600 hover:border-brand-200 transition-all">
                        {p}
                      </button>
                    ))}
                  </div>
                </div>
              )}
              {chatMessages.map((msg, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[80%] px-4 py-2.5 text-sm leading-relaxed ${msg.role === "user" ? "chat-bubble-user" : "chat-bubble-ai"}`}>
                    {msg.content}
                  </div>
                </motion.div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="chat-bubble-ai px-4 py-3 flex gap-1">
                    <span className="typing-dot w-2 h-2 rounded-full bg-brand-400" />
                    <span className="typing-dot w-2 h-2 rounded-full bg-brand-400" />
                    <span className="typing-dot w-2 h-2 rounded-full bg-brand-400" />
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="p-3 border-t border-gray-100 flex items-center gap-2 bg-white">
              <button onClick={() => setShowMoods(!showMoods)} className={`p-2 rounded-lg transition-colors ${mood ? "text-yellow-500" : "text-gray-400 hover:text-gray-600"}`}>
                <Smile className="w-5 h-5" />
              </button>
              <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendMessage()} placeholder="Ask about food, nutrition..." className="flex-1 bg-gray-50 border border-gray-200 rounded-xl px-3 py-2 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:border-brand-300" />
              <button onClick={() => sendMessage()} disabled={!input.trim() || loading} className="p-2 rounded-xl bg-brand-500 hover:bg-brand-600 disabled:opacity-40 text-white transition-all">
                {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
