# contracts

**Canonical, toolkit-owned integration contracts.** The skills don't own these — `qa-lab` does.
Each skill references this directory so the loop has a single source of truth and the parts can
evolve independently via `schema_version`.

- `review-report.schema.json` — the artifact `review-test-suite` emits and `test-suite-architect`
  ingests in its second-iteration mode. JSON Schema (draft 2020-12).
- `bug-report.schema.json` — the run artifact `bug-reporter` emits: every triaged candidate plus the
  filed / skipped-as-duplicate / rejected partitions (the precision audit trail). JSON Schema (2020-12).
- `severity-priority.yaml` — the severity scale and severity→priority mapping (shared by all three
  skills), plus the review→architect loop's gate + termination rules.

## Loop summary (v1)
generate → review #1 → human curates actions → update #1 → review #2 → human curates → update #2 → stop.
Hard cap: `max_cycles: 2`. Nothing auto-executes; the human curates the `architect_actions` set
at every gate. v1 review is **static-only** (Option A); the schema reserves a `source` field on
findings so a future dynamic reviewer (Option B) can contribute into the same artifact without a
schema break.
