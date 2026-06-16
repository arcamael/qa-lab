#!/usr/bin/env python3
"""Search a GitHub repo for an existing issue matching a candidate (the dedup gate).

Strategy (see references/deduplication.md):
  1) exact fingerprint-marker search in issue bodies (open + closed),
  2) title/error-token similarity as a hint (never an auto-match).

Shells out to `gh` (must be installed + authed). Prints JSON: {"matches": [...], "exact": bool}.
A non-empty `exact` match means: DO NOT FILE (link instead; if closed, likely a regression to flag).

Usage:
  python find_duplicates.py --repo owner/name --fingerprint bf_xxx --title "GET /rest/basket leaks basket"
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys


def _gh_search(repo: str, query: str) -> list[dict]:
    """Return issues matching a gh search query, or [] on any failure."""
    if not shutil.which("gh"):
        print("warning: gh not found; cannot dedup against the tracker", file=sys.stderr)
        return []
    cmd = [
        "gh", "issue", "list", "--repo", repo, "--state", "all", "--limit", "20",
        "--search", query, "--json", "number,title,state,url,body",
    ]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except (subprocess.SubprocessError, OSError) as e:
        print(f"warning: gh search failed: {e}", file=sys.stderr)
        return []
    if out.returncode != 0:
        print(f"warning: gh returned {out.returncode}: {out.stderr.strip()[:200]}", file=sys.stderr)
        return []
    try:
        return json.loads(out.stdout or "[]")
    except ValueError:
        return []


def _salient_tokens(title: str, n: int = 6) -> str:
    stop = {"the", "a", "an", "is", "are", "to", "of", "in", "on", "for", "and", "test", "failed"}
    toks = [t for t in title.lower().replace("/", " ").split() if t not in stop and len(t) > 2]
    return " ".join(toks[:n])


def find(repo: str, fingerprint: str, title: str) -> dict:
    # 1) exact marker — the fingerprint is embedded as `<!-- bug-fingerprint: ... -->`
    exact = _gh_search(repo, f"{fingerprint} in:body")
    if exact:
        return {"exact": True, "matches": exact, "reason": "fingerprint-marker"}
    # 2) similarity hint
    hint = _gh_search(repo, f"{_salient_tokens(title)} in:title") if title else []
    return {"exact": False, "matches": hint, "reason": "title-similarity" if hint else "none"}


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--fingerprint", required=True)
    ap.add_argument("--title", default="")
    args = ap.parse_args(argv[1:])
    json.dump(find(args.repo, args.fingerprint, args.title), sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
