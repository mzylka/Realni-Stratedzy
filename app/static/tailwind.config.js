/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["../templates/**/*.{html,js}"],
  theme: {
    extend: {
        fontFamily: {
            nunito: ["Nunito", "sans-serif"]
        }
    },
  },
  plugins: [],
}
