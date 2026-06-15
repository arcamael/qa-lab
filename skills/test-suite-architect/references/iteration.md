# Second-Iteration Mode — Applying a Review

Triggered when the skill is given a `review-report.json` produced by `review-test-suite`. The job
shifts from "generate a sample" to "revise an existing suite per the approved review."

## Inputs
- `review-report.json` (validate against `qa-lab/contracts/review-report.schema.json`).
- The existing suite on disk.
- Optionally the original generation context (the suite's own applicability map / REVIEW.md).

## The one rule that matters
Act **only** on `architect_actions` where `human_approved == true`. The human curates the queue at
the gate — editing, approving, or dropping actions. You never act on un-approved actions, and
nothing auto-executes. `remove_test` and `refactor` are not special-cased; in v1 every action type
requires approval regardless of priority.

## Procedure
1. Filter `architect_actions` to the approved subset; sort by `priority` (P0 first).
2. For each action, apply it by `action_type`, using the action's `spec` (scenarios,
   preconditions, expected_assertions) and `target`:
   - `add_test` → create at `target.suggested_path`, following house style (deterministic Playwright
     TS by default; setup at the cheapest reliable layer; assert contracts not values; idempotent
     data). New/AI-revised tests stay in the **quarantined `generated/` area**, never overwriting
     the human-verified baseline.
   - `modify_test` / `refactor` / `parameterize` → edit `target.file` / `target.test_id` in place
     within the generated area; preserve intent, improve per the linked findings.
   - `remove_test` → remove only the specified target; record why (linked findings) in the change.
   - `add_fixture` → add shared setup per the spec.
3. Carry forward all generation-mode guardrails: security tests defensive only; no compliance
   claims; no fabricated facts; secrets via environment only.
4. Keep traceability: reference the `linked_findings` ids in commit messages / change notes so each
   change traces back to its evidence.

## Loop discipline
The loop is capped at **2 cycles** (`qa-lab/contracts/severity-priority.yaml`):
generate → review #1 → (human curates) → update #1 → review #2 → (human curates) → update #2 → stop.
After applying approved actions, hand the revised suite back for the next review (if within the cap)
or for final human sign-off. Do not initiate further automated cycles beyond the cap.

## Convergence note
Because `review-test-suite` judges against this skill's own declared applicability map and risk
ranking, the two skills optimize the same objective — apply the approved actions faithfully rather
than re-litigating scope, so the suite converges instead of oscillating.
