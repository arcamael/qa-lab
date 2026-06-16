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

## Wiring Playwright MCP (in a consuming repo)
The `test-suite-architect` skill generates far more runnable tests when it can **observe the
running SUT** instead of guessing selectors. Give it that capability by registering the Playwright
MCP server in *this SUT repo* — not in `qa-lab`, which never runs against a live product.

Add a project-scoped `.mcp.json` at the SUT repo root (version-controlled, inherited by anyone who
runs Claude Code there). Register the server(s) that match the SUT's surfaces:
```jsonc
{
  "mcpServers": {
    // UI grounding — drive a browser, snapshot the accessibility tree
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest", "--browser", "chromium"]
    },
    // API grounding — read the OpenAPI/Swagger spec for real endpoints & schemas
    "openapi": {
      "command": "npx",
      "args": ["openapi-mcp-server@latest", "http://localhost:3000/api-docs/swagger.json"]
    },
    // Security grounding (STATIC only) — read SAST/SCA findings to target & measure
    // security coverage. Never an active scanner (no ZAP/Burp DAST here).
    "semgrep": {
      "command": "npx",
      "args": ["semgrep-mcp@latest"]
    },
    // Performance grounding (READ-ONLY metrics) — query SLO targets & traffic weighting
    // to pick what to load-test and set real thresholds. Never a load-runner (no k6/JMeter
    // execution here); the deliverable is the load script, run in CI.
    "prometheus": {
      "command": "npx",
      "args": ["prometheus-mcp@latest", "http://localhost:9090"]
    }
  }
}
```
With the SUT running (`export BASE_URL=...`), the skills ground **UI tests** by navigating journeys
and snapshotting the accessibility tree for real roles/labels, **API tests** by reading the OpenAPI
spec for real endpoints/schemas, **security tests** by reading static SAST/SCA findings to target the
real risk locations, and **performance tests** by querying observability metrics for real SLO targets
and traffic-weighted hot endpoints. Complementary modes: Playwright MCP observes *live behavior*;
OpenAPI and SAST/SCA MCPs read *declarative artifacts* (contract, code-risk); the metrics MCP reads
*measured current-state*. Drift, untested risk, or unmeasured hot paths are bugs the suite should
catch. **Two hard exclusions**: no active DAST (ZAP/Burp) and no load-runner (k6/JMeter execution) as
MCPs — both *run* the SUT (attacks / load), which is dynamic testing for full-coverage CI, not
grounding; security tests stay defensive and the deliverable stays a *script*, not a run. (Point each
server at your SUT's real spec/paths/endpoints and swap in whichever MCP you prefer.) MCP is for
observe-and-read only: the deliverable stays real, owned Playwright TS, grounding does not relax the
human-review gate, and `.mcp.json` is intentionally absent from `qa-lab` itself.

## Layout
```
support/        BasePage, data factories, API assertion helper
tests/api/      API contract tests (cheapest reliable layer)
tests/ui/       browser tests (only what needs a rendered UI)
```
