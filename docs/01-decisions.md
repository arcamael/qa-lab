# Decisions

## Source of truth
Git is canonical for all runnable artifacts (skills, starters, tests, orchestrator).
Craft holds a human-readable snapshot only.

## Two-repo model
- `qa-lab` — reusable toolkit (this repo). Never tests a specific product.
- `<product>-qa-lab` — one repo per SUT; consumes `qa-lab`; holds product-specific code.

Prove-then-promote: prove a pattern on a real SUT, then generalize it up into `qa-lab`.

## First instance / SUT
OWASP Juice Shop — covers functional + API + security in one Dockerized target.

## Polyglot stack
- TypeScript + Playwright = execution layer ("muscles").
- Python = AI / orchestration layer ("brain"), from Phase 2.
- Other languages added per layer as needed.

Rules: isolate each language in its own subtree with its own toolchain; couple only at
language-neutral seams.

## The seam
Playwright emits `results.json` (json reporter). The Python orchestrator consumes it.
Nothing tighter than: JSON results + test files on disk + MCP.

## Reuse model
- Skills: portable `SKILL.md`. Personal via `~/.claude/skills` symlink; team via a repo's
  committed `.claude/skills/` or a Claude Code plugin; claude.ai via upload.
- Starters: cloned/templated per new SUT.
- Knowledge: `docs/` in git (canonical) + Craft snapshot.
