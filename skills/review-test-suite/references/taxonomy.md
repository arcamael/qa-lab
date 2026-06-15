# Test-Type Taxonomy

The classifier and coverage matrix work against this list. Treat it as **extensible**: an
unrecognized category is classified `other` with a free-text label, never dropped.

## Functional family
- unit
- integration
- component
- contract (consumer-driven, e.g. Pact)
- api (request/response, schema, status, error contracts)
- e2e (system)
- smoke (build-acceptance / sanity)
- regression
- exploratory (charter-based; session-based, recognize and account for)

## Non-functional family
- performance (load, stress, soak, spike, scalability, volume)
- security
- compliance (GDPR, HIPAA, PCI-DSS, SOC 2 evidence)
- accessibility (WCAG 2.2, Section 508, EN 301 549)
- usability
- compatibility (cross-browser/device/OS, responsive)
- localization / internationalization (l10n / i18n)
- reliability (resilience, chaos, fault injection)
- recoverability (failover, backup-restore, DR)
- installability (install/upgrade/migration)

## Specialized / data family
- data-integrity (data quality, migration validation)
- visual-regression (pixel/DOM-diff, layout)
- observability (SLO validation, synthetic monitors, tests-as-monitors)
- privacy (PII handling, consent flows; overlaps compliance, track separately)
- ai-ml (model/eval-set, bias & fairness, hallucination/grounding, prompt-injection robustness,
  output-schema validation, drift)

> The taxonomy doubles as a **coverage map**: presence-and-adequacy per category turns "we have
> tests" into a defensible matrix. Absence of a category is a finding, not silence.

## Classification signals (in rough precedence)
1. Directory convention (`tests/security/`, `e2e/`, `perf/`, `a11y/`...).
2. Framework/tool (k6/JMeter → performance; axe → accessibility; Pact → contract; Playwright/
   Cypress/Selenium → e2e or component; pytest/JUnit/Jest → unit/integration/api by content).
3. Content heuristics (imports, assertions against HTTP vs DOM, load-profile config, etc.).
When signals conflict: assign a primary type plus a confidence and record the signal used.
