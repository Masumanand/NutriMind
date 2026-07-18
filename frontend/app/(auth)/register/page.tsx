"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Leaf, Mail, Lock, User, ArrowRight } from "lucide-react";
import toast from "react-hot-toast";
import { authApi } from "@/lib/api";
import { useStore } from "@/store/useStore";

const GOALS = [
  { value: "weight_loss", label: "Lose Weight", icon: "📉" },
  { value: "muscle_gain", label: "Build Muscle", icon: "💪" },
  { value: "maintenance", label: "Maintain Weight", icon: "⚖️" },
  { value: "general_health", label: "General Health", icon: "❤️" },
];

const DIETS = [
  { value: "omnivore", label: "Omnivore", icon: "🍖" },
  { value: "vegetarian", label: "Vegetarian", icon: "🥗" },
  { value: "vegan", label: "Vegan", icon: "🌱" },
  { value: "keto", label: "Keto", icon: "🥑" },
  { value: "halal", label: "Halal", icon: "☪️" },
];

export default function RegisterPage() {
  const router = useRouter();
  const { setUser, setToken } = useStore();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    email: "", username: "", password: "", full_name: "",
    goal: "general_health", diet_type: "omnivore",
  });

  const handleRegister = async () => {
    setLoading(true);
    try {
      const { data } = await authApi.register({
        email: form.email, username: form.username,
        password: form.password, full_name: form.full_name,
      });
      setToken(data.access_token);
      setUser(data.user);
      toast.success("Welcome to NutriLife! 🎉");
      router.push("/dashboard");
    } catch (err: unknown) {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || "Registration failed";
      toast.error(msg);
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-surface-primary flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-brand-500 mb-4">
            <Leaf className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">Create your account</h1>
          <p className="text-gray-500 mt-1">Step {step} of 2</p>
        </div>
        <div className="flex gap-2 mb-6">
          {[1, 2].map((s) => (
            <div key={s} className={`h-1 flex-1 rounded-full transition-all ${s <= step ? "bg-brand-500" : "bg-gray-200"}`} />
          ))}
        </div>
        <div className="glass-card p-8">
          {step === 1 && (
            <div className="space-y-5">
              <h2 className="font-semibold text-lg text-gray-800">Basic Info</h2>
              {[
                { key: "full_name", label: "Full Name", icon: User, type: "text", placeholder: "John Doe" },
                { key: "username", label: "Username", icon: User, type: "text", placeholder: "johndoe" },
                { key: "email", label: "Email", icon: Mail, type: "email", placeholder: "you@example.com" },
                { key: "password", label: "Password", icon: Lock, type: "password", placeholder: "Min 8 characters" },
              ].map(({ key, label, icon: Icon, type, placeholder }) => (
                <div key={key}>
                  <label className="block text-sm text-gray-600 mb-2">{label}</label>
                  <div className="relative">
                    <Icon className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <input type={type} value={form[key as keyof typeof form]} onChange={(e) => setForm({ ...form, [key]: e.target.value })} className="w-full bg-gray-50 border border-gray-200 rounded-xl pl-10 pr-4 py-3 text-gray-800 placeholder-gray-400 focus:outline-none focus:border-brand-400 transition-colors" placeholder={placeholder} />
                  </div>
                </div>
              ))}
              <button onClick={() => setStep(2)} disabled={!form.email || !form.username || !form.password} className="w-full py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-semibold rounded-xl flex items-center justify-center gap-2 transition-all">
                Continue <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          )}
          {step === 2 && (
            <div className="space-y-6">
              <h2 className="font-semibold text-lg text-gray-800">Your Goals</h2>
              <div>
                <label className="block text-sm text-gray-600 mb-3">What&apos;s your main goal?</label>
                <div className="grid grid-cols-2 gap-2">
                  {GOALS.map((g) => (
                    <button key={g.value} onClick={() => setForm({ ...form, goal: g.value })} className={`p-3 rounded-xl border text-sm font-medium transition-all ${form.goal === g.value ? "border-brand-500 bg-brand-50 text-brand-700" : "border-gray-200 text-gray-600 hover:border-brand-300"}`}>
                      {g.icon} {g.label}
                    </button>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-sm text-gray-600 mb-3">Dietary preference</label>
                <div className="grid grid-cols-3 gap-2">
                  {DIETS.map((d) => (
                    <button key={d.value} onClick={() => setForm({ ...form, diet_type: d.value })} className={`p-3 rounded-xl border text-sm font-medium transition-all ${form.diet_type === d.value ? "border-brand-500 bg-brand-50 text-brand-700" : "border-gray-200 text-gray-600 hover:border-brand-300"}`}>
                      {d.icon} {d.label}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex gap-3">
                <button onClick={() => setStep(1)} className="flex-1 py-3 border border-gray-200 text-gray-600 rounded-xl hover:border-gray-300 transition-all">Back</button>
                <button onClick={handleRegister} disabled={loading} className="flex-1 py-3 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white font-semibold rounded-xl transition-all">
                  {loading ? "Creating..." : "Create Account 🚀"}
                </button>
              </div>
            </div>
          )}
          <p className="text-center text-sm text-gray-500 mt-6">
            Already have an account?{" "}
            <Link href="/login" className="text-brand-600 hover:text-brand-700 font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
