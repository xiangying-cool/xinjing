/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#3B9EE8',
          light: '#5BB5F0',
          dark: '#2683CC',
        },
        teal: {
          brand: '#2EC4B6',
          light: '#4DD6CA',
        },
        orange: {
          brand: '#F5873A',
          light: '#FF9F5A',
          dark: '#E0722A',
        },
        rose: {
          soft: '#FFB7C5',
          brand: '#FF6B8A',
        },
        // 暖色系背景
        'sky-bg': '#FEF8F4',
        'mint-bg': '#FFF0F5',
        'warm-cream': '#FEF8F4',
        'warm-pink': '#FFF0F5',
        'warm-peach': '#FFF3EE',
        'warm-yellow': '#FFFBEE',
      },
      fontFamily: {
        sans: ['PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', 'sans-serif'],
      },
      backgroundImage: {
        'hero-gradient': 'linear-gradient(135deg, #FEF8F4 0%, #FFF0F5 50%, #FFFBEE 100%)',
        'blue-green': 'linear-gradient(135deg, #3B9EE8 0%, #2EC4B6 100%)',
      },
      boxShadow: {
        'card': '0 4px 20px rgba(59, 158, 232, 0.1)',
        'card-hover': '0 8px 30px rgba(59, 158, 232, 0.2)',
        'btn': '0 4px 15px rgba(245, 135, 58, 0.4)',
      },
    },
  },
  plugins: [],
}
