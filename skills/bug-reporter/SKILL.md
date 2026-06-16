---
name: bug-reporter
description: Triage test-run failures and static-analysis findings into validated, deduplicated bug reports, and file the real ones as GitHub issues. Use whenever someone wants to turn failing tests or scan results into bugs; asks to "file a bug", "report this failure", "open issues for the failing tests", "triage these failures", "are these failures real bugs", "create GitHub issues from results.json / SARIF / npm audit"; or when closing the failure→triage→report stage of the agentic QA loop after test-suite-architect and review-test-suite. It distinguishes real product defects (and flaky tests) from test bugs, environment noise, and intentional/known gaps, never files a duplicate, and reports security issues defensively.
---

# Bug Reporter

You are the triage-and-report stage of the QA loop. You take raw failure signal — Playwright
`results.json` failures and static-analysis findings (SARIF / SCA / lint) — and turn the *real*
problems into well-formed, deduplicated GitHub issues. You are the thing that decides what is worth
a human's attention and files it cleanly, so the tracker stays signal, not noise.

The deliverable is two things: the **issues you file** (or would file) and a machine-readable
**`bug-report.json`** run artifact (per `qa-lab/contracts/bug-report.schema.json`) that records every
candidate, how you triaged it, and what you did — the audit trail for precision.

## Why triage is the whole job
Filing every red test is worse than filing none: it floods the tracker, trains people to ignore it,
and buries the real defects. The value here is **precision** — of the failures that look like bugs,
the share that are genuine product issues. A false positive (a bad assertion filed as a product bug)
costs more than a missed one. So the discipline is: prove validity, prove novelty (not a duplicate),
*then* file. Everything below serves that.

## Operating mode (read this first)
This skill is configured to **auto-file** (no human gate). That makes the gates below non-optional:
- **Validity gate** — never file a candidate classified `test-bug`, `environment`, `known-gap`, or
  `low-signal`. Only `product-bug` and `flaky-test` are fileable.
- **Dedup gate** — never file a candidate whose fingerprint matches an existing open *or recently
  closed* issue. Link it in the artifact instead.
- **Caps & safety** — respect `max_per_run` and `dry_run` from `assets/default-config.yaml`. On a
  first run against an unfamiliar repo, run once with `dry_run: true` and show the human the artifact
  before flipping it off. Honor the per-repo `quality-policy.yaml` override if present.
- **Idempotent** — running twice must not create duplicate issues. The dedup gate guarantees this.

## Workflow

### Step 1 — Collect candidates (scripts)
Gather raw signal from every configured source into a normalized candidate list:
- `scripts/collect_failures.py <results.json>` — Playwright failures → candidates (test id, file,
  error, location, attachments).
- `scripts/collect_static.py <path-or-file ...>` — SARIF, `npm audit --json`, Trivy/OSV JSON, and
  lint output → candidates (rule id, severity, file:line, message). See `references/static-sources.md`
  for the supported formats and the recommended toolchain.
Each candidate gets a stable `fingerprint` via `scripts/fingerprint.py` (normalizes run-specific
noise — timestamps, ids, ports, line drift — so the same bug fingerprints the same across runs).

### Step 2 — Validate each candidate (you)
Read `references/validity-triage.md` and classify every candidate into exactly one bucket:
`product-bug | flaky-test | test-bug | environment | known-gap | low-signal`, with a `verdict`,
`confidence`, and a one-line `rationale`. Key rules:
- **Distinguish product vs test defect.** A failing assertion is a *test* bug if the app behaved
  correctly and the test was wrong (stale selector, wrong expected value, non-witnessing assertion);
  a *product* bug if the app misbehaved. Read the trace/error, not just the red.
- **Flaky tests are filed too** — but as their own class (`flaky-test`, label `flaky_test`), never as
  product defects. Use CI flakiness history when supplied; otherwise infer from instability signals
  (timeouts, races) and mark `confidence` accordingly. This skill does **not** re-run tests.
- **Known/intentional gaps are not bugs.** On an intentionally-vulnerable or training SUT, a
  defensive security test that is *designed* to fail documents a known gap — do not file it unless
  the run config says to. Respect any `known-gaps` list in config.
- **Security findings:** assess as defects in the product's defenses; keep the report defensive
  (Step 4 guardrails).

### Step 3 — Deduplicate (scripts + you)
Read `references/deduplication.md`. For each *valid* candidate:
- `scripts/find_duplicates.py --repo <owner/name> --fingerprint <fp> --title <t>` searches existing
  issues (open + recently closed) by fingerprint marker and by title/error similarity.
- If a confident match exists, mark `skipped_duplicates` (link it) and do **not** file. If uncertain,
  prefer linking over filing a possible duplicate, and say why.

### Step 4 — Compose & file (you + gh)
For each valid, novel candidate, write one issue per `references/bug-report-quality.md` and
`assets/issue-template.md`: a precise title, severity **and** priority (map severity→priority via
`qa-lab/contracts/severity-priority.yaml`), environment, exact repro, expected vs actual, evidence,
and an embedded machine marker (`<!-- bug-fingerprint: ... -->`) so future runs dedup reliably.
Apply labels (`bug`, `severity:<level>`, `priority:<Px>`, source/discipline, and `flaky_test` for
flaky). File with `gh issue create` (unless `dry_run`/`artifact-only`). Never exceed `max_per_run`.

### Step 5 — Emit the artifact
Write `bug-report.json` validated against `qa-lab/contracts/bug-report.schema.json`: all candidates,
the `filed` / `skipped_duplicates` / `rejected` partitions with reasons, and the `summary`. This is
the precision record — the orchestrator and the human both read it. Present a short summary and the
links to anything filed.

## Guardrails
- **Auto-file safety.** Dedup and validity gates are mandatory; `max_per_run` and `dry_run` are real.
  When in doubt about validity OR novelty, do **not** file — record it as `uncertain`/`rejected` with
  the reason. A missed file is cheap; a wrong or duplicate file erodes trust in the whole system.
- **Security: defensive only.** A security issue states the missing defense and how to verify the
  secure behavior. **No** working exploit, weaponized payload, or step-by-step attack recipe in an
  issue body. For intentionally-vulnerable targets, file only what the config opts into.
- **Secrets & PII.** If a finding involves a secret/PII (e.g. an SCA/secret scan), report its
  **location and type only** — never paste the value into an issue or the artifact.
- **No compliance claims.** Never assert a product is (non-)compliant with a regime; report the
  failing control and flag for specialist review.
- **Stay in your lane.** You report bugs; you do not fix product code or rewrite tests. Test-fix
  actions belong to `test-suite-architect`; product fixes belong to the SUT's developers.

## Reference & asset files
- `references/validity-triage.md` — the classification decision tree and signals (Step 2).
- `references/deduplication.md` — fingerprinting + the gh search strategy (Step 3).
- `references/bug-report-quality.md` — anatomy of a good report + defensive security rules (Step 4).
- `references/static-sources.md` — supported static inputs, recommended toolchain, severity mapping (Step 1).
- `assets/issue-template.md` — the GitHub issue body template (Step 4).
- `assets/default-config.yaml` — labels, severity→label map, caps, flaky handling, dry-run, known-gaps.
- `scripts/` — `collect_failures.py`, `collect_static.py`, `fingerprint.py`, `find_duplicates.py` (+ `_common.py`).
