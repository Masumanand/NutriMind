"use client";
import { Brain, ArrowRight } from "lucide-react";
import Link from "next/link";

interface Props {
  context: Record<string, unknown> | null;
}

export default function AiInsight({ context }: Props) {
  const suggestions = (context as Record<string, Array<{ message: string }>> | null)?.suggestions || [];
  const message = suggestions.length > 0
    ? suggestions[0].message
    : "Great job! Your protein intake is on point. Try adding more fiber-rich foods to balance your diet.";

  return (
    <div className="glass-card p-5 h-full flex flex-col justify-between bg-gradient-to-br from-brand-50 to-white">
      <div>
        <div className="flex items-center gap-2 mb-3">
          <div className="w-8 h-8 rounded-lg bg-brand-100 flex items-center justify-center">
            <Brain className="w-4 h-4 text-brand-600" />
          </div>
          <h3 className="text-sm font-semibold text-gray-800">AI Nutrition Insight</h3>
        </div>
        <p className="text-sm text-gray-600 leading-relaxed">
          {message}
        </p>
      </div>
      <Link
        href="/insights"
        className="mt-4 inline-flex items-center gap-1.5 text-sm font-medium text-brand-600 hover:text-brand-700 transition-colors"
      >
        View Full Analysis <ArrowRight className="w-3.5 h-3.5" />
      </Link>
    </div>
  );
}
