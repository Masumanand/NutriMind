"use client";
import Link from "next/link";
import {
  Brain, Scan, MessageCircle, BarChart3, Zap, Target,
  Flame, ShoppingCart, Bell, Users, ArrowRight, Leaf
} from "lucide-react";

const features = [
  { icon: Brain, title: "Smart Recommendations", desc: "AI-powered meal suggestions tailored to your goals", color: "text-green-600", bg: "bg-green-50" },
  { icon: Scan, title: "Food Scanner", desc: "Snap a photo to instantly get nutrition info", color: "text-blue-600", bg: "bg-blue-50" },
  { icon: MessageCircle, title: "AI Nutrition Coach", desc: "Chat with your personal nutrition coach", color: "text-purple-600", bg: "bg-purple-50" },
  { icon: BarChart3, title: "Health Dashboard", desc: "Track calories, macros, water with beautiful charts", color: "text-orange-600", bg: "bg-orange-50" },
  { icon: Zap, title: "Predictive Insights", desc: "See your future weight trends early", color: "text-yellow-600", bg: "bg-yellow-50" },
  { icon: Target, title: "Context-Aware", desc: "Suggestions based on your location and time", color: "text-red-600", bg: "bg-red-50" },
  { icon: Flame, title: "Habit Builder", desc: "Streaks and rewards to build healthy habits", color: "text-orange-600", bg: "bg-orange-50" },
  { icon: ShoppingCart, title: "Grocery Planner", desc: "Auto-generate weekly grocery lists", color: "text-teal-600", bg: "bg-teal-50" },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white text-gray-900 overflow-hidden">
      {/* Nav */}
      <nav className="fixed top-0 w-full z-50 border-b border-gray-100 bg-white/90 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-brand-500 flex items-center justify-center">
              <Leaf className="w-5 h-5 text-white" />
            </div>
            <span className="font-bold text-lg text-gray-900">NutriLife</span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm text-gray-500">
            <a href="#features" className="hover:text-brand-600 transition-colors">Features</a>
            <a href="#how-it-works" className="hover:text-brand-600 transition-colors">How it works</a>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login" className="text-sm text-gray-600 hover:text-gray-900 transition-colors">Sign in</Link>
            <Link href="/register" className="px-4 py-2 bg-brand-500 hover:bg-brand-600 text-white font-semibold rounded-xl text-sm transition-all">
              Get Started Free
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-5xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-brand-200 bg-brand-50 text-brand-700 text-sm mb-8">
            <Zap className="w-4 h-4" />
            <span>AI-First Nutrition Platform</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight text-gray-900">
            Your AI-Powered
            <br />
            <span className="text-brand-500">Nutrition Coach</span>
          </h1>
          <p className="text-xl text-gray-500 max-w-2xl mx-auto mb-10 leading-relaxed">
            Not just a calorie tracker. NutriLife is predictive, personalized, and behavior-driven — built to transform how you eat.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register" className="group flex items-center justify-center gap-2 px-8 py-4 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-2xl text-lg transition-all shadow-lg shadow-brand-500/20">
              Start for Free
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link href="/dashboard" className="flex items-center justify-center gap-2 px-8 py-4 border border-gray-200 hover:border-brand-300 text-gray-700 rounded-2xl text-lg transition-all hover:bg-brand-50">
              View Demo
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 px-6 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4 text-gray-900">Everything you need to eat better</h2>
            <p className="text-gray-500 text-lg">Powerful features working together</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {features.map((feature) => (
              <div key={feature.title} className="bg-white border border-gray-100 rounded-2xl p-6 hover:shadow-md transition-all">
                <div className={`w-10 h-10 rounded-xl ${feature.bg} flex items-center justify-center mb-4`}>
                  <feature.icon className={`w-5 h-5 ${feature.color}`} />
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">{feature.title}</h3>
                <p className="text-sm text-gray-500 leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-6">
        <div className="max-w-3xl mx-auto text-center bg-brand-50 border border-brand-100 rounded-3xl p-12">
          <h2 className="text-3xl font-bold mb-4 text-gray-900">Ready to transform your health?</h2>
          <p className="text-gray-500 mb-8 text-lg">Join thousands of users building healthier habits with AI</p>
          <Link href="/register" className="inline-flex items-center gap-2 px-10 py-4 bg-brand-500 hover:bg-brand-600 text-white font-bold rounded-2xl text-lg transition-all shadow-lg shadow-brand-500/20">
            Get Started — It&apos;s Free <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-100 py-8 px-6 text-center text-gray-400 text-sm">
        <p>© 2025 NutriLife. Built with ❤️ for healthier lives.</p>
      </footer>
    </div>
  );
}
