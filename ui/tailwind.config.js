/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: '#232223',     // KIT: Hintergrund
          accent: '#ff9100', // KIT: Akzent
          fg: '#ffffff',
          muted: '#9ca3af'
        }
      },
      boxShadow: { soft: '0 8px 30px rgba(0,0,0,0.12)' },
    },
  },
  plugins: [],
}
