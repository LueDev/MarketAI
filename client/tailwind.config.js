/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx}', './public/index.html'],
  theme: {
    extend: {
      colors: {
        primary: '#00c805', // Robinhood green
        dark: '#121212',
        gray: {
          100: '#f7f7f7',
          200: '#e1e1e1',
          800: '#323232',
        },
      },
    },
  },
  plugins: [],
};
