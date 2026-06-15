import { APIResponse, expect } from '@playwright/test';

/**
 * Standardizes API assertions and — importantly — failure messages, so a red test tells you
 * the status and body at a glance. SUT-specific calls (register, login) belong in the
 * instance repo; this stays generic.
 */
export async function expectOk(res: APIResponse, context = 'request'): Promise<void> {
  expect(res.ok(), `${context} failed: ${res.status()} ${await res.text()}`).toBeTruthy();
}
