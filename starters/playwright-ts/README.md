# Playwright + TypeScript Starter

Generalized baseline for testing a new SUT. Product-agnostic by design: no real selectors
or endpoints live here — those belong in your SUT repo.

## Use it for a new product
1. Copy this folder into your new SUT repo.
2. `npm install && npx playwright install`
3. Point it at the running SUT: `export BASE_URL=http://localhost:<port>`
4. Implement product-specific page objects (extend `BasePage`) and API helpers.
5. Replace the template specs under `tests/` with real ones.

## Conventions baked in (keep these)
- **Assert contracts, not exact values** — shape and invariants over brittle data.
- **Arrange state at the cheapest reliable layer** — set up via API even for UI tests, so
  a UI test fails only for UI reasons.
- **Idempotent data** — use `support/factories.ts` (`uniqueId`) so no run collides with another.
- **Page Objects** — selectors live in one place; tests read in domain language.
- **results.json is the seam** — don't remove the json reporter; the orchestrator depends on it.

## Layout
```
support/        BasePage, data factories, API assertion helper
tests/api/      API contract tests (cheapest reliable layer)
tests/ui/       browser tests (only what needs a rendered UI)
```
