# Test Discipline Taxonomy

How to decide which disciplines apply to a product, what a *sample* of each looks like, the tooling to reach for, and how each expands to full coverage. Use this in Step 2 (applicability map) and Step 3 (sample generation).

A note on scope: almost no product needs all of these. The skill is in matching disciplines to the product's actual risk, surfaces, data, and obligations. Default to *fewer, deeper* sample tests over a shallow sprawl.

## Contents
1. Functional / End-to-End
2. API / Contract / Integration
3. Data & State Integrity
4. Performance & Load
5. Security
6. Accessibility (a11y)
7. Compliance & Privacy
8. Reliability & Resilience
9. Compatibility & Localization
10. Usability & Exploratory
11. Observability & Operational
12. Visual Regression
13. AI/ML-Specific (if the product has ML/LLM features)

Each entry uses the same shape: **Applies when** · **Sample shape** · **Tooling** · **Full-coverage expansion** · **Automation**.

---

## 1. Functional / End-to-End
The core behaviors a user relies on, exercised through a real interface.
- **Applies when**: almost always — any product with user-facing behavior.
- **Sample shape**: 2-3 happy-path-plus-one-negative flows on the highest-value journeys (e.g. sign-in, the primary create/transact action). One negative case (rejected input, blocked action) per area, because failures usually fail *open*.
- **Tooling**: Playwright/Cypress (web), Appium (mobile), the product's own CLI harness.
- **Full-coverage expansion**: every journey × roles × states × edge inputs; boundary and equivalence-class analysis; cross-feature interactions.
- **Automation**: high.

## 2. API / Contract / Integration
The service contracts beneath the UI, and the seams between services.
- **Applies when**: the product exposes or consumes an API, or has more than one service.
- **Sample shape**: one positive + one negative per critical endpoint (auth: valid login returns a token; wrong password returns 401). Assert *shape/contract* — status, schema, key fields — not exact data values, which are brittle.
- **Tooling**: Playwright APIRequestContext, REST Assured, Postman/newman, Pact (consumer-driven contracts), schema validators.
- **Full-coverage expansion**: all endpoints × methods × auth states; schema/contract tests for every consumer; pagination, rate limits, error taxonomy, idempotency keys.
- **Automation**: very high — cheapest reliable layer, prefer it over UI wherever a behavior can be verified here.

## 3. Data & State Integrity
That data is correct, consistent, and survives operations.
- **Applies when**: the product persists state, has transactions, or background jobs that mutate data.
- **Sample shape**: one round-trip (create via API → verify it reads back correctly), and one idempotency/uniqueness check (re-submitting doesn't duplicate or corrupt).
- **Tooling**: API-level assertions, direct DB queries in a test env, migration test harnesses.
- **Full-coverage expansion**: referential integrity, concurrent-write/race conditions, migration up/down, soft-delete and retention behavior, money/rounding correctness.
- **Automation**: high.

## 4. Performance & Load
Behavior under realistic and stressful demand.
- **Applies when**: there are latency/throughput/availability SLOs, meaningful traffic, or a known scaling concern. **Defer** for early prototypes with no SLOs — say so explicitly.
- **Sample shape**: one baseline latency check on a key endpoint (assert p95 under a target), and one small load scenario sketch (N virtual users for M seconds) — clearly labeled as a sample to validate the *approach*, not a real capacity test.
- **Tooling**: k6, JMeter, Gatling, Locust.
- **Full-coverage expansion**: load, stress, spike, soak/endurance, scalability curves; per-SLO assertions; resource-saturation profiling.
- **Automation**: high, but environment-sensitive; usually a separate pipeline.

## 5. Security
That the product resists misuse and protects what it holds. **Defensive only** — assert defenses hold; never produce weaponized exploits.
- **Applies when**: always at a baseline; depth scales with exposure, authentication, multi-tenancy, and data sensitivity.
- **Sample shape**: one authn test (protected resource requires a valid token), one authz test (user A cannot read user B's resource — the classic IDOR/broken-object-level-auth check), and one input-handling test (a known-bad payload is *rejected or neutralized*, asserting the secure outcome).
- **Tooling**: API/UI test frameworks for authz/authn; OWASP ZAP for DAST; dependency/SCA scanners (npm audit, Snyk, Trivy); secret scanners (gitleaks).
- **Full-coverage expansion**: full OWASP Top 10 / ASVS coverage, role matrix, session and token lifecycle, rate limiting and lockout, dependency and container scanning in CI.
- **Automation**: high for authz/authn/input and SCA; DAST semi-automated; pen-test is human.

## 6. Accessibility (a11y)
That people using assistive technology can operate the product.
- **Applies when**: there's a UI, especially anything public-sector, consumer, or with accessibility obligations.
- **Sample shape**: one automated audit on a key page (axe-core, assert no critical violations), and one keyboard-only flow (tab to and submit the primary form without a mouse).
- **Tooling**: axe-core / @axe-core/playwright, Lighthouse, Pa11y; manual screen-reader passes.
- **Full-coverage expansion**: WCAG 2.2 AA across all views, focus management, ARIA correctness, contrast, screen-reader scripts.
- **Automation**: partial — automation catches ~30-40% of WCAG issues; the rest needs human verification. Say so.

## 7. Compliance & Privacy
That controls required by a regulation or standard are present and working. **Conditional and specialist** — test the controls, never certify compliance.
- **Applies when**: tied to domain and data. Map the regime to triggers:
  - **PCI-DSS** → product handles card payments.
  - **GDPR / CCPA / other privacy** → product processes personal data of residents in those jurisdictions.
  - **HIPAA** → US protected health information.
  - **SOC 2 / ISO 27001** → org-level control attestations (audit logging, access control, change management).
  - **WCAG/ADA/EAA** → accessibility obligations (overlaps with #6).
  - **Sector-specific** (e.g. financial, children's data/COPPA) as applicable.
- **Sample shape**: one control test per applicable regime — e.g. "personal-data deletion request actually removes the record" (privacy), "card PAN is never returned in an API response or log" (PCI), "security-relevant actions write an audit log entry" (SOC 2).
- **Tooling**: API/data assertions, log inspection, config/policy-as-code checks.
- **Full-coverage expansion**: the regime's full control checklist mapped to tests; data-flow and retention verification; consent and DSAR workflows. **Requires legal/compliance human sign-off** — flag this.
- **Automation**: partial; many controls are process/manual.

## 8. Reliability & Resilience
That the product degrades gracefully and recovers.
- **Applies when**: distributed system, external dependencies, or stated availability targets.
- **Sample shape**: one dependency-failure test (mock/kill a downstream and assert a graceful error, not a crash), and one retry/timeout behavior check.
- **Tooling**: fault injection / chaos tooling (Toxiproxy, Chaos Mesh), contract mocks, timeout/retry assertions.
- **Full-coverage expansion**: failover, circuit breakers, backpressure, partial-outage matrices, recovery-time objectives.
- **Automation**: medium-high.

## 9. Compatibility & Localization
That it works across the environments and locales it claims to support.
- **Applies when**: multiple supported browsers/devices/OSes, or multiple languages/regions.
- **Sample shape**: run one functional flow across two browser engines; one locale/formatting check (date/number/currency renders correctly for a non-default locale).
- **Tooling**: Playwright projects (cross-browser), BrowserStack/Sauce (device cloud), i18n linters.
- **Full-coverage expansion**: full support matrix, RTL layouts, pseudo-localization, timezone handling.
- **Automation**: high for browser/locale; device-cloud adds cost.

## 10. Usability & Exploratory
Whether the product is actually understandable and pleasant — and what scripted tests miss.
- **Applies when**: any product with human users; exploratory always adds value on unfamiliar products.
- **Sample shape**: a short charter-based exploratory test session plan (time-boxed, with a mission), plus 2-3 noted heuristics to probe. Largely manual.
- **Tooling**: session-based test management notes; the human tester.
- **Full-coverage expansion**: structured exploratory charters per area, usability studies.
- **Automation**: low — this is deliberately human; do not pretend otherwise.

## 11. Observability & Operational
That the system tells the truth about itself in production.
- **Applies when**: the product is operated as a service with logs/metrics/alerts.
- **Sample shape**: one test asserting a key action emits the expected structured log/metric; one health-check/readiness-probe test.
- **Tooling**: log/metric assertions, synthetic monitors, smoke tests.
- **Full-coverage expansion**: alert-correctness tests, SLO burn-rate checks, dashboard validation, synthetic journeys in prod.
- **Automation**: medium.

## 12. Visual Regression
That the UI doesn't break visually in ways functional tests miss.
- **Applies when**: UI with meaningful layout/branding, or frequent style churn.
- **Sample shape**: one snapshot of a key page/component with a sensible diff threshold.
- **Tooling**: Playwright toHaveScreenshot, Applitools, Percy, Chromatic.
- **Full-coverage expansion**: component-library coverage, responsive breakpoints, theme/state matrices.
- **Automation**: high, but needs baseline governance to avoid noise.

## 13. AI/ML-Specific
For products with ML models or LLM-powered features — increasingly common, and easy to under-test.
- **Applies when**: the product contains a model, an LLM call, RAG, or agentic behavior.
- **Sample shape**: one eval-style test on a fixed input set (assert quality/accuracy threshold on a small labeled set), and one safety test (e.g. a prompt-injection attempt is resisted; the model refuses an out-of-scope request).
- **Tooling**: eval harnesses, golden datasets, LLM-as-judge with caution, guardrail/jailbreak test sets.
- **Full-coverage expansion**: regression evals across versions, bias/fairness slices, hallucination and grounding checks, adversarial/jailbreak suites, latency/cost budgets.
- **Automation**: medium — outputs are non-deterministic, so assert distributions/thresholds, not exact strings.
