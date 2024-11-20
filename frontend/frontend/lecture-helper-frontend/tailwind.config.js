module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'], // Ensure this points to your React components
  theme: {
    extend: {},
  },
  plugins: [require('@tailwindcss/forms')],

};
