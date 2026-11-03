import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: process.env.BASE_PATH || '/',
  server: process.env.VITE_PROXY_TARGET ? {
    allowedHosts: ['frontend'],
    proxy: { '/api': { target: process.env.VITE_PROXY_TARGET, changeOrigin: true } },
  } : undefined,
})
