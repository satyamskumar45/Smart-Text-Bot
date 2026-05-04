/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        body: ["DM Sans", "sans-serif"],
        display: ["Syne", "sans-serif"],
        mono: ["DM Mono", "monospace"],
      },
      colors: {
        ink: "#080c12",
        panel: "#141e2e",
        mint: "#63d2be",
        ocean: "#4f8ef7",
        amberSoft: "#f5a623",
      },
      boxShadow: {
        glow: "0 18px 60px rgba(99, 210, 190, 0.14)",
      },
    },
  },
  plugins: [],
};
