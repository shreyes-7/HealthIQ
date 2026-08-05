import path from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// Polyfill webidl for undici / jsdom compatibility in Node environment
if (typeof globalThis.webidl === 'undefined') {
  globalThis.webidl = { util: { markAsUncloneable: (o) => o } }
} else if (globalThis.webidl.util && typeof globalThis.webidl.util.markAsUncloneable !== 'function') {
  globalThis.webidl.util.markAsUncloneable = (o) => o
}

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  server: {
    port: 5173,
  },
  test: {
    environment: 'jsdom',
    globals: false,
    setupFiles: ['./src/test-setup.js'],
  },
})
