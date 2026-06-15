# contracts

**Canonical, toolkit-owned integration contracts.** Neither `review-test-suite` nor
`test-suite-architect` owns these — `qa-lab` does. Both skills reference this directory so the
review→architect loop has a single source of truth and the two can evolve independently via
`schema_version`.

- `review-report.schema.json` — the artifact `review-test-suite` emits and `test-suite-architect`
  ingests in its second-iteration mode. JSON Schema (draft 2020-12).
- `severity-priority.yaml` — the severity scale, the severity→priority mapping the architect
  schedules by, and the loop's gate + termination rules.

## Loop summary (v1)
generate → review #1 → human curates actions → update #1 → review #2 → human curates → update #2 → stop.
Hard cap: `max_cycles: 2`. Nothing auto-executes; the human curates the `architect_actions` set
at every gate. v1 review is **static-only** (Option A); the schema reserves a `source` field on
findings so a future dynamic reviewer (Option B) can contribute into the same artifact without a
schema break.
