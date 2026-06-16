# Static-Analysis Sources

This skill does not run scanners; it **consumes their output** (the language-neutral seam) and turns
real findings into bug candidates. Standardize on **SARIF** — the OASIS standard most static tools can
emit — plus a couple of common JSON formats. The SUT decides which scanners to run; the skill stays
tool-agnostic.

## Recommended toolchain (what to point at each concern)
| concern | tools (suggested) | output the skill reads |
|---|---|---|
| Security SAST (code) | Semgrep, CodeQL, ESLint security plugins | SARIF |
| Dependencies / SCA | `npm audit --json`, OSV-Scanner, Trivy, Snyk | npm-audit JSON, OSV/Trivy JSON, or SARIF |
| Secrets | gitleaks, trufflehog | SARIF (gitleaks `--report-format sarif`) |
| Functional / code bugs | ESLint, `tsc --noEmit`, language analyzers (ruff, vet, …) | SARIF, or parsed tool text |
| Performance | **primarily the k6/load *results*, not static** | perf result JSON (treat separately) |

Honesty note on the edges: deep **functional** bugs and real **performance** regressions are found by
*tests*, not static analysis. Static gives you bug *patterns* (null-deref, unhandled rejection,
injection sink) and dependency CVEs reliably; treat "performance issue found statically" as a weak
signal (a few anti-pattern lint rules) and lean on the load-test results for the real number.

## SARIF mapping (the primary format)
For each `runs[].results[]`:
- `ruleId` → candidate `location.rule_id`; the rule's `shortDescription` → message.
- `level` (`error|warning|note`) → severity: `error→major` (or higher if the rule is security-tagged:
  `→critical`), `warning→minor`, `note→info`. A rule tagged `security`/`cwe` lifts one level.
- `locations[].physicalLocation` → `location.file` (repo-relative) + region (start line).
- `partialFingerprints` / `fingerprints`, when present, feed the dedup fingerprint directly.

## SCA mapping
- `npm audit --json`: each advisory → one candidate; `severity` (`critical|high|moderate|low`) →
  `critical→critical`, `high→major`, `moderate→minor`, `low→info`; title = "`<pkg>@<range>`: <CVE/title>".
  Collapse all advisories for one package into one issue.
- Trivy/OSV JSON: vulnerability id (CVE/GHSA) + package + fixed version → one defensive candidate.

## Severity is advisory, judgment is final
Tool severities are a starting point; re-rate by **actual blast radius in this SUT** (an injection sink
on a public unauthenticated endpoint outranks the same rule in dead code). Record the tool's original
level in evidence so the re-rating is auditable.

## De-noising (critical for auto-file)
Static tools are noisy. Before filing: drop suppressed/baseline findings, collapse same-rule-same-cause
clusters into one issue, and gate info/style findings to `low-signal`. Filing one issue per lint hit is
exactly the tracker-flooding failure this skill exists to prevent.
