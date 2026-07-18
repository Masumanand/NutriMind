import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "react-hot-toast";

export const metadata: Metadata = {
  title: "NutriLife – Smart Food & Health Companion",
  description: "AI-powered nutrition tracking, meal planning, and health insights",
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster
          position="top-right"
          toastOptions={{
            style: {
              background: "#ffffff",
              color: "#1a2e1f",
              border: "1px solid #e8efe9",
              borderRadius: "12px",
              boxShadow: "0 4px 12px rgba(0,0,0,0.08)",
            },
            success: { iconTheme: { primary: "#3b8a4a", secondary: "#ffffff" } },
            error: { iconTheme: { primary: "#ef4444", secondary: "#ffffff" } },
          }}
        />
      </body>
    </html>
  );
}
