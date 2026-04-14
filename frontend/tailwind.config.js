/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg:     "#05101E",
        surf:   "#0A1828",
        up:     "#0F2038",
        border: "#1A3352",
        cyan:   "#00D4C8",
        red:    "#FF3347",
        gold:   "#F5C030",
      },
    },
  },
  plugins: [],
};
