# Test Smell Catalog

Named smells with detection heuristics (what `scripts/detect_smells.py` looks for) and the fix the
architect should apply. Heuristics are deliberately conservative — better a missed smell than a
false accusation. Each detected instance becomes a finding with a default severity (overridable by
policy) and maps to a dimension.

| smell id | dimension | heuristic (static) | default severity | fix / directive |
|----------|-----------|--------------------|------------------|-----------------|
| fixed-sleep | D4 | `waitForTimeout`, `time.sleep`, `Thread.sleep`, `cy.wait(<number>)` | critical | replace with explicit wait/poll on a condition or locator |
| missing-assertion | D3 | test body with no `expect`/`assert`/`should`/`verify` call | blocker | add an assertion that verifies the stated behavior |
| hardcoded-secret | D6/D11 | password/api-key/token/secret assigned a string literal; high-entropy literals; `Authorization: Bearer ...` | blocker | move to env/secret store; report location+type ONLY, never the value |
| conditional-logic | D2/D14 | `if`/`for`/`while`/`switch` inside a test body | major | split into separate/parameterized tests; tests must be straight-line |
| order-dependence | D5 | module/class-level mutable state mutated by tests; reliance on declaration order; shared fixtures without isolation | critical | isolate state; make each test set up its own preconditions |
| assertion-roulette | D3 | many assertions in one test, none with messages | minor | add failure messages or split; identify which assert failed |
| eager-test / over-assertion | D3/D2 | one test exercising many unrelated behaviors | minor | one behavior per test |
| skipped-debt | D9 | `@skip`/`xit`/`it.skip`/`@Ignore`/`@pytest.mark.skip`/`.only` | major (`.only` = critical) | re-enable or delete with rationale; never ship `.only` |
| mystery-guest | D6 | reads external files/fixtures/DB not declared in setup | major | bring data into the test or a named factory/fixture |
| slow-test | D8 | (needs runtime; static proxy: many network/E2E ops) | info | flag for the future dynamic reviewer |
| tautological-assert | D3 | `toBeTruthy()`/`assertTrue(true)`/`assert x == x` style; asserting a constant | critical | assert the actual contract (decode token, check field, status code) |

## Notes for the detector
- Identify the test body span first (framework-aware: `test(...)`, `it(...)`, `def test_*`,
  `@Test`), then scan within it — this avoids flagging helper/util code.
- For `missing-assertion`, count assertion calls inside the body; zero = finding. Be aware some
  frameworks assert implicitly (e.g. Playwright `expect`), so key off known assertion APIs.
- For secrets, NEVER include the matched value in output; emit `evidence` as the line location and
  a category label (e.g. "bearer-token literal"). This is a hard safety rule.
