/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'cyan': {
          500: '#06b6d4',
        },
      },
      boxShadow: {
        'lg-cyan': '0 10px 15px -3px rgba(6, 182, 212, 0.2), 0 4px 6px -2px rgba(6, 182, 212, 0.1)',
      },
    },
  },
  plugins: [],
};