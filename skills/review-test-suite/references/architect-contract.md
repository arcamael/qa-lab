# Architect Handoff Contract

The canonical schema and severity→priority mapping live in **`qa-lab/contracts/`** — this file is a
usage guide, not a second source of truth. Always validate the emitted artifact against
`qa-lab/contracts/review-report.schema.json`.

## What the architect consumes
`test-suite-architect` (in its second-iteration mode) reads `architect_actions` where
`human_approved == true`. It ignores `findings`/`coverage_gaps` for *execution* (those are
human-facing and for traceability), acting only on the curated action queue.

## Making actions executable (the one job that matters)
Each action's `spec` must let the architect implement without re-deriving intent:
- `action_type`: add_test | modify_test | remove_test | refactor | add_fixture | parameterize
- `target`: suggested_path for new tests; file + test_id for changes
- `linked_findings`: ids of the findings/gaps that justify it (traceability both ways)
- `spec`: `test_type`, concrete `scenarios`, `preconditions`, `expected_assertions`
- `priority`: from the severity→priority map
- `human_approved`: emitted as `false`; the human gate flips the approved ones

Bad: "improve the auth tests." Good: action add_test, security, scenarios ["reject expired JWT",
"lock account after N failed logins"], preconditions ["seeded user U-1"], expected_assertions
["401 on expired token", "lockout (423) after threshold"].

## Cross-linking & stability
- `findings`, `coverage_gaps`, `architect_actions` cross-link by id so a human can trace any action
  to its evidence and back.
- Ids and ordering must be **stable** across runs over unchanged input (sort by dimension, then
  severity, then location) so reports diff cleanly for CI gating and trend tracking.

## Loop discipline
Max 2 cycles. Nothing auto-executes. `remove_test`/`refactor` are not special-cased — in v1 every
action needs human approval regardless of priority.
