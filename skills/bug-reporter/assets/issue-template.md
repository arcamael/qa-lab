<!-- bug-fingerprint: {{fingerprint}} -->
<!-- filed-by: bug-reporter skill · source: {{source}} -->

**Severity:** {{severity}}  ·  **Priority:** {{priority}}  ·  **Discipline:** {{discipline}}

## Summary
{{one-sentence what-is-wrong-and-where}}

## Environment
- SUT: {{repo}} @ `{{commit}}`
- Target: `{{base_url}}` ({{env}})
- Surface: {{browser/project or endpoint}}
- Observed via: {{test id or static tool + rule}}

## Steps to reproduce
{{numbered, minimal, deterministic — prefer a copy-pasteable command}}
```
{{repro command, e.g. npx playwright test path/to.spec.ts -g "title"  OR  curl ...}}
```

## Expected
{{the contract / the secure or correct behavior}}

## Actual
{{what happened — concrete: status, shape, state}}

## Evidence
{{pointers: trace/screenshot/log excerpt/SARIF region — quote only the relevant lines}}

---
<!--
  TEMPLATE NOTES (delete before filing):
  - One bug per issue. If you wrote "and also", split it.
  - flaky_test: frame as a test-reliability problem (instability signal + suspected cause + fix
    direction), not a product defect.
  - security: DEFENSIVE ONLY. State the missing defense + how to verify the secure behavior + the
    CWE/OWASP category. NO working exploit/weaponized payload/attack recipe. Secrets/PII: location +
    type only, never the value. No compliance claims.
  - Keep the bug-fingerprint marker at the top — it is the exact dedup key for future runs.
-->
