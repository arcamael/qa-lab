# Roadmap

1. **Foundation** — deploy SUT locally; hand-write a deterministic Playwright baseline
   (UI + API). Establishes ground truth and the benchmark. (Done for Juice Shop.)
2. **AI-assisted** — add Playwright MCP; have an LLM generate candidate tests from the
   product's features; diff against the baseline to measure quality.
3. **Single agent** — automate one stage end-to-end (generation OR failure triage) in CI.
4. **Multi-agent** — orchestrate generation → execution → triage → self-heal, with a
   human-review gate and an observability dashboard.
5. **Tune & govern** — guardrails, coverage/flake metrics, and the review workflow:
   the QA-manager-over-agents seat.

Each phase = a documented milestone + write-up = portfolio evidence.
