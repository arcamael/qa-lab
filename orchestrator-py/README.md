# orchestrator-py

The Python "brain" of the lab (Phase 2+). It does **not** run tests — it reasons over their
results. The contract is the language-neutral seam: it reads the `results.json` that the
TypeScript Playwright suite emits, and (later) drives test generation, failure triage, and
self-heal via the Anthropic API and Playwright MCP.

Today it contains just the results reader — the first half of the seam — with tests, so the
contract is real from day one.

## Dev
```bash
pip install -e '.[dev]'
pytest -q
```
