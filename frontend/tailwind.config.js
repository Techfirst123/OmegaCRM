/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50:  '#e8f0fb',
          100: '#c5d9f5',
          200: '#9bbde8',
          300: '#6fa1dc',
          400: '#4d8dd3',
          500: '#0d5cab',
          600: '#0b52a0',
          700: '#094690',
          800: '#073a7f',
          900: '#0c213d',
          950: '#071629',
        },
        surface: {
          50:  '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        card:       '0 1px 3px 0 rgba(0,0,0,.08), 0 1px 2px -1px rgba(0,0,0,.06)',
        'card-hover':'0 4px 6px -1px rgba(0,0,0,.1), 0 2px 4px -2px rgba(0,0,0,.06)',
        sidebar:    '4px 0 24px rgba(0,0,0,.08)',
      },
    },
  },
  plugins: [],
}
