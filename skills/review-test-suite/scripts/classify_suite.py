#!/usr/bin/env python3
"""Walk a test suite, detect languages/frameworks, and classify each file by taxonomy type.
Usage: python classify_suite.py <path> [--out FILE]
Emits JSON: {files:[...], summary:{languages, frameworks, test_counts_by_type, total_tests}}.
"""
from __future__ import annotations
import argparse, json, sys
from collections import Counter
import _common as C


def run(root: str) -> dict:
    files = C.discover_test_files(root)
    out_files, langs, fws, types = [], Counter(), Counter(), Counter()
    for f in files:
        text = C.read(f)
        lang = C.detect_language(f)
        frameworks = C.detect_frameworks(text)
        ttype, conf, signal = C.classify_type(f, text, frameworks, root if not root == f else ".")
        langs[lang] += 1
        for fw in frameworks:
            fws[fw] += 1
        types[ttype] += 1
        out_files.append({
            "path": f, "language": lang, "frameworks": frameworks,
            "test_type": ttype, "confidence": conf, "signal": signal,
            "n_tests": sum(1 for _ in C.iter_tests(text, lang)),
        })
    return {
        "files": out_files,
        "summary": {
            "languages": sorted(langs),
            "frameworks": sorted(fws),
            "test_counts_by_type": dict(types),
            "total_files": len(files),
            "total_tests": sum(f["n_tests"] for f in out_files),
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--out")
    a = ap.parse_args()
    result = run(a.path)
    payload = json.dumps(result, indent=2)
    if a.out:
        open(a.out, "w").write(payload)
    else:
        print(payload)
    if result["summary"]["total_files"] == 0:
        sys.stderr.write("no tests detected: path has no recognizable test files\n")


if __name__ == "__main__":
    main()
