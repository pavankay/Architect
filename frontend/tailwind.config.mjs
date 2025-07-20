/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}'],
  theme: {
    extend: {
      fontFamily: {
        'mono': ['TG Frekuent Mono', 'monospace'],
        'roboto': ['Roboto', 'system-ui', 'sans-serif'],
      },
      colors: {
        'black': '#000000',
        'white': '#FFFFFF',
      }
    },
  },
  plugins: [],
}