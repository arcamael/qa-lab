---
name: review-test-suite
description: Review an existing test suite and produce a structured, evidence-backed quality assessment — for humans (a readable scorecard with prioritized risks) and for the test-suite-architect skill (a machine-readable work queue of precise fixes). Use whenever someone wants to review, audit, critique, or grade tests; asks "are our tests any good", "find coverage gaps", "what's wrong with this test suite", "review my tests"; or when closing the review→fix loop with test-suite-architect. Performs STATIC analysis only — it reads tests, it does not run them. It is the evaluation half of the agentic QA loop.
---

# Review Test Suite

You evaluate a test suite — across all test types — against a modern QA quality model, and emit
**one canonical artifact** (`review-report.json`) plus a human report rendered from it. This skill
is the *critic* in a generate→review→update loop with `test-suite-architect`. It does not write
tests and it does not run them; it produces evidence-backed findings and a precise, actionable
work queue the architect implements after a human curates it.

## Scope (v1, Option A)
- **Static only.** Read test files and optional auxiliary inputs. Do NOT execute tests or the SUT.
- Where dynamic data exists (coverage report, CI flakiness history), **consume it as input** to
  raise confidence — never generate it. The schema reserves `source: "static" | "dynamic"` on
  findings so a future dynamic reviewer can contribute into the same artifact; v1 emits `"static"`.

## The most important principles
- **Anchor to the architect's own declared scope.** When reviewing output from `test-suite-architect`,
  hold it to *its own* applicability map and risk ranking first (did it deliver what it said it
  would, at the quality it implied?), then flag what it missed. Reviewing against a different rubric
  makes the loop oscillate instead of converge.
- **Deterministic facts come from scripts; judgment comes from you.** The `scripts/` do
  classification, smell detection, metric computation, and rendering — reproducibly and cheaply.
  You are reserved for what genuinely needs reasoning: risk weighting, prioritization, gap
  rationale, scoring synthesis, and ambiguous classification. Never hand-compute what a script
  computes; never hand-write the report the renderer produces.
- **No false confidence.** If you lack the input to judge a dimension (e.g. no coverage report for
  D1), say so and lower that dimension's `confidence` rather than guessing a score.
- **Absence is a finding.** "Zero security tests" is a high-risk coverage gap, not silence.
- **Findings cite evidence**; **actions are executable**. A finding without a file/test/line is
  weak; an action whose `spec` makes the architect re-derive intent has failed its one job.

## Workflow

### Step 1 — Intake & classify (scripts)
Run `scripts/classify_suite.py <path>` to walk the tree, detect languages/frameworks, and classify
each file by the taxonomy in `references/taxonomy.md`. Note any auxiliary inputs the user supplied
(requirements, risk register, coverage report, CI/flakiness history, repo quality policy). Missing
aux inputs lower confidence; they are not errors.

### Step 2 — Gather deterministic facts (scripts)
Run, against the same path:
- `scripts/detect_smells.py` — static anti-patterns / test smells (see `references/smell-catalog.md`).
- `scripts/compute_metrics.py` — pyramid distribution, redundancy, assertion stats, skipped count,
  flakiness-risk index.
- `scripts/build_coverage_matrix.py` — presence/adequacy/risk per taxonomy category.
These emit JSON to stdout (or a file). Treat their output as ground-truth facts you reason over.

### Step 3 — Judge (you)
Read `references/quality-model.md` (the 14 dimensions, D1–D14) and the active policy
(`assets/default-policy.yaml`, overridden by a repo `quality-policy.yaml` if present). For each
dimension: synthesize the script facts into a 0–100 score with a `confidence`, attach findings with
severity (`blocker|critical|major|minor|info`) and an effort estimate, and — where coverage is
absent or weak — write `coverage_gaps` with concrete missing scenarios and a rationale tied to
requirements/risk when available.

### Step 4 — Build the architect work queue (you)
Translate findings and gaps into `architect_actions` per `references/architect-contract.md` (the
canonical schema lives at `qa-lab/contracts/`). Each action: a type, target, priority (via the
severity→priority map), linked findings, and a `spec` precise enough to implement blind
(scenarios, preconditions, expected_assertions). Set `human_approved: false` on every action.

### Step 5 — Emit + render
Assemble `review-report.json`, validate it against `qa-lab/contracts/review-report.schema.json`,
then run `scripts/render_report.py review-report.json > review-report.md`. The human report is
ALWAYS rendered from the JSON — never hand-written — so the two views cannot disagree.

### Step 6 — Human gate (hand off, do not loop)
Present the report. The human **curates the `architect_actions`** — editing, approving, or dropping
them — and sets `human_approved: true` on the ones to apply. Only then does `test-suite-architect`
run its second-iteration mode on the approved subset. Respect the loop cap: **at most 2 cycles**
(`qa-lab/contracts/severity-priority.yaml`). Nothing auto-executes.

## Guardrails
- **Static only** — never run the tests or the SUT in this skill.
- **Secret safety** — when a secret/PII is detected (D6/D11), report its *location and type only*;
  never echo the value into findings or the report.
- **Security of coverage, not of the SUT** — you assess whether security *tests* exist and are
  sound; you do not scan the application's runtime security.
- **No auto-execution, no destructive autonomy** — `remove_test`/`refactor` and everything else
  require human approval regardless of priority in v1.

## Reference & asset files
- `references/taxonomy.md` — test-type taxonomy (Step 1).
- `references/quality-model.md` — the D1–D14 dimensions + scoring rubric (Step 3).
- `references/smell-catalog.md` — named smells, detection heuristics, fixes (Step 2/3).
- `references/architect-contract.md` — the handoff schema + conventions (Step 4); canonical copy in `qa-lab/contracts/`.
- `assets/report-template.md` — the human report skeleton the renderer fills.
- `assets/default-policy.yaml` — default dimension weights, severity thresholds, profiles.
