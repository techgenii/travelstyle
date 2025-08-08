/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Semantic colors that map to CSS variables
        primary: 'var(--color-primary)',
        secondary: 'var(--color-secondary)',
        accent: 'var(--color-accent)',
        background: 'var(--color-background)',
        surface: 'var(--color-surface)',
        'text-primary': 'var(--color-text-primary)',
        'text-secondary': 'var(--color-text-secondary)',
        success: 'var(--color-success)',
        warning: 'var(--color-warning)',
        error: 'var(--color-error)',
        border: 'var(--color-border)',
        
        // Light variations for backgrounds
        'primary-light': 'var(--color-primary-light)',
        'secondary-light': 'var(--color-secondary-light)',
        'accent-light': 'var(--color-accent-light)',
        'success-light': 'var(--color-success-light)',
        'warning-light': 'var(--color-warning-light)',
        'error-light': 'var(--color-error-light)',
      },
      transitionDuration: {
        '300': '300ms',
      }
    },
  },
  darkMode: 'class',
  plugins: [require('tailwind-scrollbar')],
};
