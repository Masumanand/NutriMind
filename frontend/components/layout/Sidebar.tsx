"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Brain, Calendar, UtensilsCrossed,
  ShoppingCart, TrendingUp, BarChart3, Settings, LogOut, Leaf
} from "lucide-react";
import { useStore } from "@/store/useStore";
import clsx from "clsx";

const NAV_ITEMS = [
  { href: "/dashboard", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/insights", icon: Brain, label: "AI Analysis" },
  { href: "/planner", icon: Calendar, label: "Meal Planner" },
  { href: "/scanner", icon: UtensilsCrossed, label: "Recipes" },
  { href: "/habits", icon: ShoppingCart, label: "Grocery List" },
  { href: "/predict", icon: TrendingUp, label: "Progress" },
  { href: "/social", icon: BarChart3, label: "Reports" },
  { href: "/chatbot", icon: Settings, label: "Settings" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useStore();

  return (
    <aside className="fixed left-0 top-0 h-full w-[240px] bg-white border-r border-gray-100 flex flex-col z-40">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-6 py-5 border-b border-gray-50">
        <div className="w-9 h-9 rounded-xl bg-brand-500 flex items-center justify-center">
          <Leaf className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="font-bold text-base text-gray-900">NutriLife</span>
          <p className="text-[10px] text-gray-400 -mt-0.5">Eat Better. Live Better.</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map(({ href, icon: Icon, label }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          return (
            <Link
              key={href}
              href={href}
              className={clsx(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all text-sm",
                active
                  ? "bg-brand-50 text-brand-600 font-semibold"
                  : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
              )}
            >
              <Icon className={clsx("w-[18px] h-[18px]", active && "text-brand-500")} />
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Upgrade Card */}
      <div className="mx-4 mb-4 p-4 bg-brand-50 rounded-xl border border-brand-100">
        <p className="text-xs font-semibold text-brand-700 mb-1">Upgrade to Premium</p>
        <p className="text-[11px] text-brand-600/70 leading-relaxed mb-3">
          Unlock advanced AI insights, custom meal plans, and more.
        </p>
        <button className="w-full py-2 bg-brand-500 hover:bg-brand-600 text-white text-xs font-semibold rounded-lg transition-colors">
          Upgrade Now →
        </button>
      </div>

      {/* User + Logout */}
      <div className="px-4 py-3 border-t border-gray-100">
        {user && (
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-brand-100 flex items-center justify-center text-xs font-bold text-brand-700">
              {(user.full_name || user.username)[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{user.full_name || user.username}</p>
              <p className="text-[11px] text-gray-400 truncate">Level {user.level}</p>
            </div>
            <button
              onClick={logout}
              className="p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 transition-all"
              title="Sign out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="px-6 py-3 border-t border-gray-50">
        <p className="text-[10px] text-gray-300">© 2025 NutriLife. All rights reserved.</p>
        <p className="text-[10px] text-gray-300">Privacy Policy · Terms of Service</p>
      </div>
    </aside>
  );
}
