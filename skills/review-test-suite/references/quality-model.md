# Quality Model — Dimensions D1–D14

Each dimension yields a 0–100 score, a `confidence`, findings, and evidence. Scores are synthesized
by Claude from the deterministic script facts plus judgment; weights come from the active policy.
Every dimension is assessed even when it scores low due to *absence* — "not present" must be
distinguishable from "present but weak" (set confidence accordingly and explain).

| # | Dimension | What it checks (illustrative) | Primary script inputs |
|---|-----------|------------------------------|------------------------|
| D1 | Coverage & traceability | requirement/risk coverage, code coverage if provided, boundary/equivalence, negative & error paths, traceability links, API endpoint coverage vs spec, perf coverage of traffic-weighted hot paths | coverage_matrix, aux coverage report, requirements, aux API spec (OpenAPI), aux observability/APM metrics |
| D2 | Test design quality | AAA / Given-When-Then, single responsibility, intention-revealing names, no control flow in tests, Page Object/Screenplay, parameterization vs copy-paste | smells, metrics |
| D3 | Assertion quality | assertions present, specific, meaningful messages, no over-assertion / assertion roulette, soft vs hard, perf thresholds match real SLOs | smells, metrics (avg_assertions), aux SLO targets |
| D4 | Determinism & flakiness risk | fixed sleeps vs explicit waits, time/locale/random seeding, external/network reliance, race conditions, order dependence; cross-ref CI flakiness if supplied | smells, metrics (flakiness_index), aux CI history |
| D5 | Isolation & independence | any-order & parallel safe, clean setup/teardown, no shared mutable state, no leaked fixtures | smells (order-dependence), metrics |
| D6 | Test data management | factories/builders vs hardcoded, deterministic seeds, NO secrets/PII in tests, env-config hygiene | smells (hardcoded-secret, hardcoded-data), aux SAST/secret-scan findings |
| D7 | Maintainability | DRY, naming, duplicate/redundant/dead tests, readability, comment hygiene, fixture reuse | metrics (redundancy), smells |
| D8 | Pyramid / distribution & efficiency | unit:integration:e2e balance, ice-cream-cone, redundant high-cost tests, parallelizability | metrics (pyramid) |
| D9 | Reliability & quarantine strategy | retry sanity, flaky-test quarantine, skipped/xit/@Ignore debt | metrics (skipped_count), smells |
| D10 | CI/CD & tooling readiness | tagging for selective runs, reporting/artifacts, deterministic envs, fail-fast strategy | classify (config files), policy |
| D11 | Security-of-tests & security coverage | secrets in code (cross-ref D6), insecure fixtures, AND whether security scenarios exist (authz/authn, injection, secrets handling), tested vs real risk locations | smells, coverage_matrix, aux SAST/SCA findings |
| D12 | Compliance & regulatory traceability | compliance-relevant requirements mapped to evidence-producing tests, audit-trail readiness | coverage_matrix, requirements |
| D13 | Observability of failures | diagnostics on failure (logs, screenshots, traces, HARs), debuggability, failure attribution | classify (config), smells |
| D14 | Anti-pattern / test-smell catalog | named smells: mystery guest, eager test, fragile test, conditional logic, interdependence, slow test, obscure test | smells |

## Scoring guidance
- Start each dimension at the evidence: a script fact (e.g. "12 fixed sleeps across 38 e2e tests")
  drives the score and a finding, not a vibe.
- **D3 — the "witness test" for false greens (judgment, not static).** An assertion can pass without
  exercising the behavior under test — e.g. asserting an element is visible when that element is
  present in *both* the pass and fail states (a logged-out vs logged-in nav button), so the test is
  green even when the feature is broken. The static detector won't catch this (it needs to know the
  app's states), so it is a reviewer heuristic: for each assertion ask **"would this target actually
  differ between the behavior working and the behavior broken?"** If not, the assertion is a false
  green — flag it (distinct from `tautological-assert`, which asserts a constant). Prefer assertions
  on a state that only the success path produces (a session token, a post-action URL, created data).
- A dimension with no input to judge it → low `confidence`, score stated as provisional, and a note
  in the appendix. Do not invent a number.
- Overall health = policy-weighted mean of dimension scores. Document the formula in the report.
  Overall `confidence` = lowest band among dimensions that carry material weight.
- Map severity→priority via `qa-lab/contracts/severity-priority.yaml`. The loop gate (stop when
  zero blockers/critical and no major coverage gaps; hard cap 2 cycles) lives there too.
