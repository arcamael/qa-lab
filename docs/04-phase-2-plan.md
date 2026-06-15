# Phase 2 — AI-assisted test generation & scoring

## Goal
Add the AI-assisted layer on top of the deterministic Phase 1 baseline. Have the Python
orchestrator drive an LLM (Anthropic API) plus Playwright MCP to **generate candidate tests**
against the SUT (Juice Shop), then **score those candidates against the hand-written baseline**
using the existing `results.json` reader. The output is a scorecard and a set of candidate tests
for human review — not auto-merged coverage.

This phase proves the central value proposition: with a human-verified baseline as ground truth,
"the AI wrote N tests" becomes measurable ("the AI reproduced X baseline behaviors, found Y new
ones, with Z false positives").

## The contract (unchanged)
Orchestrator ↔ suite communicate only via: `results.json` (Playwright json reporter), test files
on disk, and Playwright MCP. Nothing tighter.

## Task 0 — Environment & contract sanity (do first)
- Both repos install cleanly; `juiceshop-qa-lab` suite is green against a running Juice Shop
  (`docker run --rm -p 3000:3000 bkimminich/juice-shop`); `orchestrator-py` tests pass.
- Run the Juice Shop suite, then confirm `summarize(load_report("results.json"))` reports the
  correct counts for that real run.
- **Acceptance:** the orchestrator parses a real Juice Shop `results.json` and the numbers match
  what Playwright reported.

## Task 1 — Wire Playwright MCP
- Add the Playwright MCP server (`npx @playwright/mcp@latest`) so an agent can drive a real
  browser against the SUT via the accessibility tree.
- **Acceptance:** an agent can navigate `http://localhost:3000`, read page structure, and perform
  a login through MCP.

## Task 2 — Grounded test generation
- Add an `orchestrator-py` module that, given a target (base URL + a feature/flow description, or
  flows discovered via MCP and the products API), calls the Anthropic API to generate candidate
  Playwright **TypeScript** tests that follow the starter conventions, written to a `generated/`
  directory in the instance repo (quarantined — never mixed into the baseline).
- **Ground the generation** in the app's actual structure (MCP exploration, the `/api/Products`
  shape, real selectors) rather than letting the model guess. Grounding is what separates ~90%
  executable output from ~30%.
- Default model: `claude-sonnet-4-6` (good cost/quality for code-gen); confirm current model
  strings against the Claude API docs.
- **Acceptance:** generated tests are valid TypeScript, run under Playwright, and the grounded
  ones pass against Juice Shop.

## Task 3 — Score against the baseline
- Run both the hand-written baseline and the generated suite; use the `results.json` reader to
  compute the metrics below and emit a **scorecard** (`scorecard.json` + a readable `scorecard.md`).
- **Acceptance:** a scorecard artifact comparing AI-generated vs baseline on the defined metrics.

## Task 4 — Human-review gate
- Present candidates + scorecard for human review. Nothing from `generated/` is promoted into the
  real suite without explicit approval — same sample-first discipline the `test-suite-architect`
  skill enforces.
- **Acceptance:** a clear review artifact; no auto-merge path exists.

## Metrics (define these precisely in code)
- **Baseline reproduction rate** — % of baseline behaviors the AI suite also covers.
- **Net-new coverage** — behaviors the AI covered that the baseline lacks (promotion candidates).
- **Precision** — of AI tests that fail, the share that are real product issues vs bad assertions
  (false positives). This is the most important and the hardest number.
- **Stability** — flake rate of generated tests across N repeated runs.

## Guardrails
- Generated tests live in `generated/`; the baseline is read-only ground truth.
- Security tests defensive only; no compliance claims.
- `ANTHROPIC_API_KEY` from environment; never commit a key.

## Out of scope (defer to Phase 3+)
- Failure-triage and self-healing agents, CI integration of the agent loop, multi-agent
  orchestration, observability dashboard. Phase 2 ends at "generate + score + human review."
