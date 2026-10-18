/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        cyber: {
          bg: "#080c14",
          surface: "#0e1422",
          card: "#141d30",
          border: "#1f2b45",
          accent: "#00e5ff",
          blue: "#38bdf8",
          darkblue: "#0284c7",
          warning: "#f59e0b",
          danger: "#ef4444",
          success: "#10b981",
          muted: "#64748b"
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "Fira Code", "Consolas", "monospace"]
      }
    },
  },
  plugins: [],
}
