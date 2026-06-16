# Bug Report Quality

A good report lets a developer reproduce and fix without a conversation. One bug per report; if you're
writing "and also", split it. Optimize for **actionability**, not length.

## Anatomy (every fileable issue)
- **Title** — specific and searchable: *what* is wrong *where*, not "test failed". Good:
  "`GET /rest/basket/:id` returns another user's basket (BOLA)". Bad: "auth test broken".
- **Severity & priority** — both. Severity (`blocker|critical|major|minor|info`) by blast radius ×
  likelihood; priority (`P0–P4`) via `qa-lab/contracts/severity-priority.yaml`. State them up front.
- **Environment** — SUT commit/version, base URL/env, browser/project, OS, and how the failure was
  observed (which test / which tool). Reproducibility dies without this.
- **Steps to reproduce** — numbered, minimal, deterministic. Prefer a copy-pasteable command
  (`npx playwright test <spec> -g "<title>"`, or the API call) over prose.
- **Expected vs actual** — the contract vs what happened, concretely (status codes, shapes, states).
- **Evidence** — pointers to the trace, screenshot, failing assertion, log excerpt, or SARIF region.
  Quote the *relevant* lines; don't paste a 500-line log.
- **Fingerprint marker** — embed `<!-- bug-fingerprint: <fp> -->` in the body (enables exact dedup).
- **Labels** — `bug`, `severity:<level>`, `priority:<Px>`, a source/discipline label
  (`security`, `performance`, `accessibility`, `api`, `ui`), and `flaky_test` for flaky tests.

## Flaky-test reports
Frame as a **test-reliability** problem, not a product defect: which test, the instability signal
(retry-pass, timeout, race), suspected cause, and the suggested fix direction (explicit wait, isolate
state, seed time/random). Label `flaky_test`. Severity by how much it erodes CI trust.

## Security reports — defensive only
Security issues protect the product; they must not become an attack manual.
- **Do** state: the missing/!weak defense, the affected endpoint/component, the impact class
  (e.g. "broken object-level authorization"), and **how to verify the secure behavior** (the
  assertion that should hold). Reference the CWE/OWASP category by name.
- **Do not** include: a working exploit, a weaponized or copy-pasteable attack payload, credential
  dumps, or a step-by-step "how to compromise" recipe. A defensive repro that asserts the *secure*
  outcome (and currently fails) is the right form.
- **Secrets/PII**: report **location and type only** ("AWS key committed at `config/x.ts:42`"), never
  the value. Same for any PII surfaced by a finding.
- **No compliance claims.** Report the failing control ("audit log missing for deletion"); never write
  "this is GDPR/PCI-non-compliant". Flag for specialist review.

## Don't-file checklist (mirror of the validity gate)
Before filing, confirm it is **not**: a test bug, an environment issue, a known/intentional gap, a
low-signal nit, or a duplicate. If any of those, it goes to `rejected`/`skipped_duplicates` in the
artifact with a reason — not into the tracker.
