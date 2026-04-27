/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ['"JetBrains Mono"', 'monospace'],
        sans: ['"DM Sans"', 'sans-serif'],
      },
      colors: {
        ink: {
          50:  '#f0f0f2',
          100: '#d8d8de',
          200: '#b0b0bc',
          300: '#88889a',
          400: '#606078',
          500: '#383856',
          600: '#2a2a44',
          700: '#1c1c32',
          800: '#0e0e20',
          900: '#07070f',
        },
        acid: {
          DEFAULT: '#00ff88',
          dim: '#00cc6a',
        },
        amber: {
          rag: '#ffaa00',
        }
      }
    }
  },
  plugins: []
}
