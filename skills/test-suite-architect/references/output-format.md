# Output Format, House Style & Templates

Use in Step 3 (generating the sample) and Step 4 (the review packet). The goal of every convention here is *reviewability*: a human should be able to open the output and understand the approach in minutes.

## Sample directory layout

Lay the sample out so disciplines are visible at a glance and code-vs-spec is separated:

```
<product>-sample-suite/
├── REVIEW.md                      # the human-review packet (the centerpiece — Step 4)
├── README.md                      # how to install deps and run the sample
├── tests/
│   ├── functional/                # one folder per applicable discipline
│   ├── api/
│   ├── security/
│   ├── performance/               # may hold a k6 script rather than a *.spec
│   ├── accessibility/
│   └── <discipline>/ ...
├── specs/                         # non-code disciplines: checklists, charters, control lists
│   ├── compliance-controls.md
│   └── exploratory-charters.md
└── support/                       # shared helpers, fixtures, page objects, config
```

Only create folders for disciplines marked **applies**. Don't scaffold empty disciplines — their absence is information the reviewer should see reflected in REVIEW.md, not as empty directories.

## House style (defaults — adapt to the product's actual stack)

Match the product's existing conventions when they exist. When starting fresh, default to:

- **Web UI + API**: TypeScript + Playwright (one framework spanning UI via browser and API via `request`). Page Objects for UI; thin data/helper factories for setup.
- **Setup at the cheapest layer**: arrange state via API even for UI tests, so a UI test fails only for UI reasons.
- **Idempotent data**: generate unique test data per run; never depend on or mutate shared fixed records.
- **Assert contracts, not values**: shape and invariants over exact inventory/data, which is brittle.
- **Deterministic & owned code**: real test files the team versions, not opaque runtime interpretation.
- **Machine-readable results**: emit a JSON report (e.g. Playwright's `json` reporter to `results.json`) so an orchestrator can consume outcomes downstream.
- **Performance**: k6 scripts. **Security authz/authn/input**: the same test framework as API. **a11y**: axe-core. **Visual**: framework-native snapshots.
- **Non-code disciplines** (usability, manual compliance controls): a concrete Markdown checklist or charter in `specs/`, plus any automatable subset as code.
- **Ground selectors in reality**: when a Playwright MCP server was used to explore the running SUT, base UI locators on the observed accessibility-tree roles/labels rather than guessed CSS; selectors you could not verify against a live instance belong in the Assumptions list, not presented as fact.

If the product's stack makes a different choice clearly better (Python service → pytest + httpx + Playwright-python; gRPC → buf/ghz; mobile → Appium), use it and note the deviation in REVIEW.md.

## Annotation convention

Every sample test carries a short header comment so the reviewer understands intent without reading the implementation. Keep it to three lines:

```
// WHAT: a registered user can log in through the UI and reach an authenticated state
// WHY-THIS-PRODUCT: auth gates every user journey; broken login = total outage (risk rank 1)
// FULL-COVERAGE: + SSO/OAuth providers, lockout after N failures, session expiry, password reset
```

For `specs/` items, lead each checklist with the same WHAT / WHY-THIS-PRODUCT / FULL-COVERAGE framing in prose.

## REVIEW.md template

Generate this exactly, filled in from the product and the sample. This is what the human reads to steer the work.

```markdown
# Test Suite Review — <Product>

## 1. Product understanding
2-4 sentences: what it is, primary journeys, what "broken" costs. Surfaces and stack in one line each.

## 2. Applicability map
| Discipline | Verdict | Risk rank | Rationale (tied to product facts) |
|---|---|---|---|
| Functional | Applies | 1 | ... |
| API | Applies | 2 | ... |
| Security | Applies | 3 | ... |
| Performance | Defer | — | no SLOs defined yet; revisit before launch |
| Compliance: PCI | N/A | — | no card data handled |
| ... | ... | ... | ... |

## 3. What's in this sample
Per applicable discipline: how many tests, what they demonstrate, where they live. Make clear this is a representative slice, not coverage.

## 4. Assumptions
Everything inferred rather than confirmed. Each item is something the reviewer can correct.
- Assumed the API base URL is http://localhost:3000 (not confirmed).
- Assumed registration accepts {email, password}; not verified against a running instance.

## 5. Open questions
Decisions that change the approach and that I could not resolve myself.
- Are there SLOs that would make performance testing in-scope now?
- Which user roles exist? The authz sample assumes exactly two.

## 6. Full-coverage plan
Per applicable discipline: rough test count, tooling, key expansions, dependencies, and a rough effort signal (S/M/L). This is the menu the reviewer approves or edits before full generation.

## 7. Recommended next adjustments
Your honest read: where to go deeper, what to cut, the weakest assertion in the sample, the biggest risk currently uncovered.
```

## Sizing guardrail

A sample is typically ~1-3 tests per applicable discipline and rarely more than ~15-20 artifacts total, regardless of product size. If the sample is growing past that before the review gate, you've drifted into full-coverage behavior — stop and write REVIEW.md.
