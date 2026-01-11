/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    darkMode: 'class',
    theme: {
        extend: {
            colors: {
                background: '#0a0a0a', // Slightly darker
                surface: '#121212',
                primary: '#ec4899', // Pink-500-ish (Neon Pink)
                secondary: '#a855f7', // Purple-500 (Neon Purple)
                accent: '#d946ef', // Fuchsia-500
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
        },
    },
    plugins: [],
}
