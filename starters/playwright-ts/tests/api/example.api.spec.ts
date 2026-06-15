import { test } from '@playwright/test';
import { expectOk } from '../../support/api';

/**
 * TEMPLATE — replace with your SUT's real endpoints.
 * WHAT: a representative API contract check (shape, not exact values).
 * Set BASE_URL, then adapt the path and assertions.
 */
test.describe('API contract — template', () => {
  test('a root/health endpoint responds', async ({ request }) => {
    const res = await request.get('/'); // TODO: point at a real endpoint
    await expectOk(res, 'GET /');
  });
});
