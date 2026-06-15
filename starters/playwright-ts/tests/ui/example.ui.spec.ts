import { test, expect } from '@playwright/test';
import { BasePage } from '../../support/BasePage';

/**
 * TEMPLATE — replace with your SUT's real journey.
 * WHAT: a representative UI smoke check using the BasePage convention.
 */
test('the app loads', async ({ page }) => {
  const base = new BasePage(page);
  await base.goto('/'); // dismissOverlays() is a no-op until overridden per SUT
  await expect(page).toHaveTitle(/.*/); // TODO: assert something real
});
