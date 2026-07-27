import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/procurement': { target: 'http://localhost:8000', changeOrigin: true },
    },
    // Allow hot-reload to stay alive longer for chat streaming future use
    hmr: { timeout: 30000 },
  },
})
