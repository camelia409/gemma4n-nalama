/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                brand: {
                    green: '#2D7A4F',
                    red: '#C0392B',
                    yellow: '#F39C12',
                    bg: '#F8F9FA',
                    text: '#2C3E50',
                }
            },
            fontFamily: {
                tamil: ['"Noto Sans Tamil"', 'sans-serif'],
            }
        },
    },
    plugins: [],
}
