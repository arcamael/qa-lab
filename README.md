# qa-lab

Reusable QA toolkit — **skills, starters, and shared tooling** to stand up an AI-assisted
QA process on *any* product.

This repo is the **toolkit**, never a place where tests run against a specific product.
Each product-under-test (SUT) gets its own repo (e.g. `juiceshop-qa-lab`) that *consumes*
this one.

## Layout

```
qa-lab/
├── skills/               # portable Claude skills (SKILL.md + references)
│   └── test-suite-architect/
├── starters/             # clone-me scaffolds for a new SUT
│   └── playwright-ts/     # generalized Playwright + TS baseline (own toolchain)
├── packages/             # shared helpers, extracted from starters when reuse appears
├── orchestrator-py/       # Phase 2+: Python "brain" that reads results.json (own toolchain)
├── docs/                 # canonical knowledge (Craft holds a snapshot; this is source of truth)
└── .github/workflows/    # per-language CI: ci-ts.yml, ci-py.yml
```

## How the pieces relate: prove-then-promote

- A SUT repo is an **instance**: real tests against one product, with product-specific
  selectors and endpoints.
- `qa-lab` is the **toolkit**: the generalized patterns those instances share.
- Flow: discover a pattern while testing a real product → once it's proven, generalize it
  *up* into `qa-lab` (a starter or a skill) → future instances consume it.
- **Canonical-copy rule:** for any shared asset, `qa-lab` owns the one true copy. Instances
  import or extend it; they never keep a divergent fork. Product-specific code stays in the
  instance.

## Using the skills

A skill is a portable `SKILL.md` folder that works across Claude.ai, Claude Code, and the API.

- **Personal (this machine, all projects):** symlink it into your personal skills folder:
  ```bash
  ln -s "$(pwd)/skills/test-suite-architect" ~/.claude/skills/test-suite-architect
  ```
  Edit once here; every Claude Code project sees the change. Note: a symlink is a local
  convenience — it does **not** travel to other machines/teammates or to claude.ai.
- **Team (travels with a repo):** commit the skill into that repo's `.claude/skills/`.
- **Bundle/distribute:** add a `.claude-plugin/plugin.json` to ship it as a Claude Code plugin.
- **claude.ai:** upload the skill folder in the app (per-account; no org-wide distribution).

## Using the starter

See `starters/playwright-ts/README.md`. In short: copy it into a new SUT repo, set
`BASE_URL`, implement the SUT-specific page objects and API helpers, and replace the
template specs — keeping the conventions intact.

## Polyglot rules (why TS + Python + others coexist cleanly)

This is a polyglot monorepo. It stays maintainable because of two rules:

1. **Isolate each language in its own subtree** with its own toolchain. `starters/playwright-ts`
   has its own `package.json`/`node_modules`; `orchestrator-py` has its own `pyproject.toml`/venv.
   The repo is polyglot; each subtree is monoglot.
2. **Couple across languages only at language-neutral seams** — JSON files, test files on disk,
   CLI invocations, HTTP, MCP. The Python orchestrator talks to the TS suite through
   `results.json` and `npx playwright test`, never through shared in-memory objects.

Heavy polyglot build tools (Bazel, Pants, Nx) are deliberately **not** used yet — plain
folder-per-language plus per-language CI is the right amount of structure until build
orchestration actually hurts.

## CI

Two independent jobs, one per language subtree:
- `ci-ts.yml` — installs and type-checks the starter, lists tests.
- `ci-py.yml` — installs and tests the orchestrator.

(End-to-end runs against a live product belong in the *instance* repos, not here.)
