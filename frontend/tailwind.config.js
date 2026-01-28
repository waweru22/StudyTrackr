/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        josefin: ['"Josefin Sans"', 'sans-serif'],
        'dm-sans': ['"DM Sans"', 'sans-serif'],
      },
      boxShadow: {
        'sidebar': '0 4px 60px 0 rgba(0, 0, 0, 0.05)',
      }
    },
  },
  plugins: [],
}
