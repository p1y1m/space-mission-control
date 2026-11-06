import { defineConfig } from '@playwright/test'
const chromiumExecutable = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH
export default defineConfig({
  testDir: './e2e',
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:5173',
    trace: 'on-first-retry',
    launchOptions: chromiumExecutable ? { executablePath: chromiumExecutable } : undefined,
  },
  webServer: process.env.E2E_BASE_URL ? undefined : { command: 'npm run dev', url: 'http://localhost:5173', reuseExistingServer: true },
})
