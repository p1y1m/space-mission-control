import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: process.env.GITHUB_ACTIONS ? '/space-mission-control/' : '/',
  server: process.env.VITE_PROXY_TARGET ? {
    allowedHosts: ['frontend'],
    proxy: { '/api': { target: process.env.VITE_PROXY_TARGET, changeOrigin: true } },
  } : undefined,
})
