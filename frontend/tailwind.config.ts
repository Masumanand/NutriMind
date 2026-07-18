import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f0f9f1",
          100: "#e0f2e2",
          200: "#c3e5c6",
          300: "#93d09a",
          400: "#5cb868",
          500: "#3b8a4a",
          600: "#2d6b38",
          700: "#25562e",
          800: "#1f4526",
          900: "#1a3920",
        },
        surface: {
          primary: "#f8faf9",
          card: "#ffffff",
          hover: "#f0f7f1",
        },
        text: {
          primary: "#1a2e1f",
          secondary: "#4b6852",
          muted: "#8fa898",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
      animation: {
        "fade-in": "fadeIn 0.3s ease-in-out",
        "slide-up": "slideUp 0.4s ease-out",
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
      },
      keyframes: {
        fadeIn: { "0%": { opacity: "0" }, "100%": { opacity: "1" } },
        slideUp: { "0%": { transform: "translateY(20px)", opacity: "0" }, "100%": { transform: "translateY(0)", opacity: "1" } },
      },
    },
  },
  plugins: [],
};

export default config;
