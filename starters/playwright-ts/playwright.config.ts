import { defineConfig, devices } from '@playwright/test';

/**
 * Generalized starter config. Two things are deliberate and should survive into any SUT:
 *  - baseURL comes from BASE_URL so the same suite runs against any environment.
 *  - the json reporter writes results.json — the language-neutral seam the Python
 *    orchestrator reads. Keep it.
 */
export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
    ['json', { outputFile: 'results.json' }],
  ],
  use: {
    baseURL: process.env.BASE_URL ?? 'http://localhost:3000',
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  projects: [
    { name: 'api', testDir: './tests/api' },
    {
      name: 'chromium-ui',
      testDir: './tests/ui',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});
