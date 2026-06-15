# CLAUDE.md — qa-lab

Project memory for Claude Code. Read this and `docs/` before starting work.

## What this repo is
`qa-lab` is a **reusable QA toolkit** — skills, starters, shared tooling — for standing up an
AI-assisted QA process on any product. It is the *toolkit*, **never** a place where tests run
against a specific product. Each product-under-test (SUT) lives in its own repo and consumes
this one. The first instance is `juiceshop-qa-lab` (expected as a sibling directory).

## Current work
**Phase 2 — AI-assisted test generation & scoring.** Read `docs/04-phase-2-plan.md`. That file
is the source of truth for what to build next, in what order, with acceptance criteria.

## Layout
- `skills/test-suite-architect/` — portable Claude skill: generates a *sample* multi-discipline
  test suite for a product, for human review before full coverage. Has a second-iteration mode
  that ingests a `review-report.json` and applies human-approved `architect_actions`.
- `skills/review-test-suite/` — portable Claude skill: statically reviews an existing suite and
  emits a `review-report.json` (findings + curated `architect_actions`), the reviewer counterpart
  that closes the generate→review→update loop with `test-suite-architect`.
- `contracts/` — toolkit-owned, language-neutral seam both skills reference: the
  `review-report.schema.json` artifact contract and `severity-priority.yaml` (severity scale,
  severity→priority mapping, loop gate + termination rules). `qa-lab` owns the one true copy.
- `starters/playwright-ts/` — generalized Playwright + TypeScript baseline. Own toolchain
  (`package.json`). Product-agnostic; copied into a SUT repo and specialized there.
- `orchestrator-py/` — the Python "brain" (Phase 2+). Own toolchain (`pyproject.toml`). Reads
  Playwright `results.json`; will drive generation, triage, self-heal. Currently holds the
  results reader + tests.
- `packages/` — placeholder for helpers extracted from starters once reuse is proven. Empty by design.
- `docs/` — canonical knowledge. Git is source of truth; Craft holds a human-readable snapshot.

## How to work in each subtree
- TypeScript: `cd starters/playwright-ts && npm install && npx tsc --noEmit` (type-check) /
  `npx playwright test --list`. Running e2e needs a live SUT (belongs in the instance repo).
- Python: `cd orchestrator-py && pip install -e '.[dev]' && pytest -q`.

## Conventions to uphold (do not silently break these)
- **Polyglot rule 1 — isolate by subtree.** Each language keeps its own toolchain in its own
  folder. Never a shared root mixing them.
- **Polyglot rule 2 — couple only at language-neutral seams.** The seam is `results.json` +
  test files on disk + MCP. The Python orchestrator must not reach into TS internals; it reads
  the JSON report and edits/invokes test files via the CLI.
- **Deterministic & owned.** Generated tests are real Playwright TS following the starter
  conventions, version-controlled, not opaque runtime magic.
- **Assert contracts, not exact values.** Shape and invariants over brittle data.
- **Cheapest reliable layer.** API/contract checks before browser checks.
- **Idempotent data.** Unique test data per run; never depend on or mutate shared records.
- **Keep the json reporter** in `playwright.config.ts` — the orchestrator depends on it.
- **Prove-then-promote / canonical copy.** Generalize patterns up from an instance into here;
  for any shared asset, this repo owns the one true copy.

## Guardrails
- Security tests are **defensive only** — assert that defenses hold; never produce weaponized
  exploits. For intentionally-vulnerable targets, asserting the *secure* behavior (which then
  fails, documenting the gap) is fine.
- Never claim a product "is compliant" with any regime; only test supporting controls and flag
  where specialist review is needed.
- **Secrets via environment only.** Use `ANTHROPIC_API_KEY` from the environment; never hardcode
  or commit a key. The human enters credentials; you do not.
