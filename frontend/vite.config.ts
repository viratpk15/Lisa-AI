import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5174,
    proxy: {
      '/chat': 'http://127.0.0.1:8000',
      '/conversations': 'http://127.0.0.1:8000',
      '/tools': 'http://127.0.0.1:8000',
      '/prompts': 'http://127.0.0.1:8000',
      '/rag': 'http://127.0.0.1:8000',
      '/agents': 'http://127.0.0.1:8000',
      '/memory': 'http://127.0.0.1:8000',
      '/models': 'http://127.0.0.1:8000',
      '/workflows': 'http://127.0.0.1:8000',
      '/deployments': 'http://127.0.0.1:8000',
      '/auth': 'http://127.0.0.1:8000',
      '/api': 'http://127.0.0.1:8000',
    },
  },
})
