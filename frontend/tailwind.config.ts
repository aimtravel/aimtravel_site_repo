import type { Config } from "tailwindcss";

/**
 * Токените идват от CSS променливи в src/styles/tokens.css, а не са
 * записани тук като hex стойности. Така shadcn/ui компонентите работят
 * без промяна, а бранд палитрата се сменя на едно място.
 */
export default {
  darkMode: ["class"],
  content: [
    "./src/**/*.{ts,tsx}",
    // Django template-и, които съдържат Tailwind класове:
    "../templates/**/*.html",
  ],
  theme: {
    container: { center: true, padding: "1.5rem", screens: { "2xl": "1120px" } },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: { DEFAULT: "hsl(var(--primary))", foreground: "hsl(var(--primary-foreground))" },
        secondary: { DEFAULT: "hsl(var(--secondary))", foreground: "hsl(var(--secondary-foreground))" },
        destructive: { DEFAULT: "hsl(var(--destructive))", foreground: "hsl(var(--destructive-foreground))" },
        muted: { DEFAULT: "hsl(var(--muted))", foreground: "hsl(var(--muted-foreground))" },
        accent: { DEFAULT: "hsl(var(--accent))", foreground: "hsl(var(--accent-foreground))" },
        popover: { DEFAULT: "hsl(var(--popover))", foreground: "hsl(var(--popover-foreground))" },
        card: { DEFAULT: "hsl(var(--card))", foreground: "hsl(var(--card-foreground))" },
        // Бранд токени извън shadcn контракта
        navy: { 500: "#2C5B87", 700: "#12395F", 800: "#0D2B47", 900: "#071726" },
        coral: "#E8635C",
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 4px)",
        sm: "calc(var(--radius) - 8px)",
      },
      fontFamily: {
        display: ["Montserrat", "system-ui", "sans-serif"],
        sans: ["Manrope", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
