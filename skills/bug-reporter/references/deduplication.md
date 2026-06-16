# Deduplication

Filing a duplicate is a precision failure as bad as filing a non-bug. Because this skill auto-files,
dedup is a **hard gate**: a valid candidate is filed only after it clears this check. Idempotency —
running the skill twice produces no second issue — falls out of doing this correctly.

## The fingerprint
Every candidate carries a `fingerprint` (from `scripts/fingerprint.py`): a short hash over the
**stable** parts of the failure, with run-specific noise normalized away so the *same* bug fingerprints
identically across runs and machines.

Normalized before hashing:
- timestamps, durations, UUIDs/hex ids, ports, temp paths, line/column numbers that drift,
- generated test data (emails like `qa.lab+<digits>@…`, `Date.now()` ids),
- absolute paths → repo-relative.

Kept (the signal):
- **test failures:** normalized test title + spec file (basename) + normalized error class/message
  (e.g. `expect(received).toBe` + status code), not the full stack.
- **static findings:** tool + `rule_id` + repo-relative file + symbol/function (not raw line number).

The fingerprint is embedded in every filed issue as an HTML comment marker:
`<!-- bug-fingerprint: <fp> -->`. That marker is the primary, exact dedup key on future runs.

## The search (gh)
`scripts/find_duplicates.py --repo <owner/name> --fingerprint <fp> --title "<t>"` does, in order:
1. **Exact marker search** — `gh issue list --search "<fp> in:body" --state all` (include closed: a
   recently-closed bug that recurs may be a regression, but is still "already known" — link, and note
   it may need reopening rather than a fresh file).
2. **Title/error similarity** — search by the salient error tokens and normalized title; surface the
   top candidates for you to judge. Similarity is a *hint*, not an auto-match.

## Deciding
- **Confident match** (marker hit, or unmistakable same failure) → `skipped_duplicates`, link the
  existing issue, do not file. If it was closed and is failing again, say so: likely a regression to
  reopen — flag it rather than silently opening a new one.
- **Possible match** (similar title, no marker) → prefer linking over filing. If you file anyway,
  reference the possible-duplicate in the body and explain why it's distinct.
- **No match** → novel; proceed to file.
- **Within a single run**, collapse candidates that share a fingerprint (or one root cause) into one
  issue before any of them is filed — don't file N issues for one defect.

## Why include closed issues
A defect filed, fixed, and closed that fingerprints again is a **regression** — valuable signal, but
not a brand-new discovery. Linking/reopening preserves history; a fresh duplicate destroys it.
