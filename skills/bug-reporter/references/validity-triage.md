# Validity Triage

How to classify a candidate. The goal is **precision**: only `product-bug` and `flaky-test` are
fileable; everything else is recorded in the artifact's `rejected` partition with a reason. When the
evidence is thin, classify `uncertain` and **do not file** — a missed bug is cheaper than a wrong one.

## The six classes

| class | fileable? | what it means | tell-tale signals |
|---|---|---|---|
| `product-bug` | ✅ | the app misbehaved; the test correctly caught it | assertion on a real product response failed; error/trace shows the SUT returning the wrong status/shape/state; reproducible |
| `flaky-test` | ✅ (label `flaky_test`) | the test passes and fails without code change | passes on retry; timeout/race wording; intermittent in CI history; timing-dependent locator |
| `test-bug` | ❌ | the app was fine; the **test** is wrong | stale/incorrect selector, wrong expected value, non-witnessing assertion, bad setup/fixture, hardcoded data that drifted |
| `environment` | ❌ | infra/config, not the product | connection refused, 502 from a proxy, missing env var, SUT not running, DB unseeded, port conflict |
| `known-gap` | ❌ (unless config opts in) | a failure that is expected by design | defensive security test on an intentionally-vulnerable/training SUT; a test asserting a not-yet-built feature; anything on the config `known-gaps` list |
| `low-signal` | ❌ | real but not worth a tracker entry | info-level lint, style nits, duplicate of a broader finding already filed this run |

## Product bug vs test bug — the core distinction
This is where most false positives come from. For each failing assertion, ask **"did the app do the
wrong thing, or did the test expect the wrong thing?"**
- Read the **trace/error and the actual response**, not just the red. A `401` where the contract says
  `200` is a product bug; a `200` the test wrongly expected to be `404` is a test bug.
- **Non-witnessing assertions** (an assertion that passes/fails regardless of the behavior under test —
  e.g. checking an element present in both logged-in and logged-out states) make a red meaningless:
  classify the underlying failure `uncertain` and flag the test instead.
- **Selector/contract drift**: if the only evidence is "element not found" and the app clearly still
  works, lean `test-bug` unless the missing element *is* the regression.

## Flaky tests (filed, separately)
- Strongest signal: a recorded **pass on retry** in the same run, or a supplied CI flakiness history
  showing intermittency. Use those when present.
- Static signals (lower confidence): fixed sleeps, time/locale/random reliance, network races,
  "Target closed"/timeout wording, order dependence.
- File flaky tests as their own issue (label `flaky_test`, severity usually `minor`/`major` by blast
  radius), titled as a *test reliability* problem, not a product defect. Never let a flaky red be
  filed as a product bug — that is a precision failure in the other direction.
- This skill is **static**: it does not re-run tests to confirm flakiness. State the confidence and
  the signal you used.

## Static-analysis candidates (SAST/SCA/lint)
- A SAST finding is a `product-bug` candidate when it identifies a real defect class (injection sink,
  auth flaw, null-deref, unhandled rejection) at a real location. Severity comes from the tool mapped
  via `references/static-sources.md`.
- An SCA/dependency finding (CVE in a dependency) is fileable as a `product-bug` (security) — but keep
  it defensive: name the package/version/CVE and the remediation, not an exploit.
- Lint/style/info findings are usually `low-signal` unless they encode a real bug pattern.
- De-noise: collapse many findings of the same rule at the same root cause into **one** issue with a
  list, not N issues. That collapse is itself a dedup decision (see deduplication.md).

## Severity (then priority)
Assign severity on the five-level scale (`blocker|critical|major|minor|info`) by **blast radius ×
likelihood**, then map to priority via `qa-lab/contracts/severity-priority.yaml`. A broken auth/payment
path or an exploitable security gap is `blocker`/`critical`; a cosmetic or single-edge-case issue is
`minor`/`info`. Flaky tests are rated by how much they erode CI trust, not by the feature they touch.
