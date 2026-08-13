#!/usr/bin/env python3
"""Score our problem tags against the `union/` ground truth.

Joins `union/<slug>/meta.json` to the bank (both content roots) by slug, then by
title, plus a small hand-verified rename table for problems whose slug *and*
title drifted. For the overlapping problems, both tag lists go through
`app.tags.normalize_tags` and are compared as sets.

Since `scripts/apply_union_tags.py` ran, this should score 1.000 on the matched
subset — it is now a regression guard (has anything drifted back?) rather than a
measurement. It still reports the union problems we don't have at all.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.tags import DROPPED_TAGS, normalize_tags  # noqa: E402

# Hand-verified renames: union slug -> our slug (same problem, different slug+title).
RENAMES = {
    "alien-dictionary": "alien-dictionary-order",
    "design-hit-counter": "hit-counter",
    "design-in-memory-file-system": "in-memory-file-system",
    "design-search-autocomplete-system": "autocomplete-top-k",
    "find-eventual-safe-states": "eventual-safe-states",
    "find-median-from-data-stream": "median-from-data-stream",
    "find-the-duplicate-number": "find-duplicate-number",
    "maximum-profit-in-job-scheduling": "maximum-profit-job-scheduling",
    "search-insert-position": "binary-search-insert-position",
    "kth-largest-element-in-an-array": "kth-largest-element",
    "meeting-rooms-ii": "meeting-rooms-required",
    "convert-sorted-array-to-binary-search-tree": "sorted-array-to-bst",
    "web-crawler": "web-crawler-same-host",
}


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def load(root: Path) -> dict[str, dict]:
    out = {}
    for meta in sorted(root.glob("*/meta.json")):
        out[meta.parent.name] = json.loads(meta.read_text())
    return out


def canon(tags: list[str]) -> set[str]:
    """Both sides, in our vocabulary.

    Every fold this used to apply by hand now lives in app/tags.py, so the union
    side goes through exactly the same normalizer our own writes do. A union tag
    list that survives to nothing (e.g. only `database`) returns the empty set --
    normalize_tags would otherwise report its ["math"] fallback as an opinion.
    """
    raw = [x.strip().lower() for x in (tags or []) if x and x.strip()]
    if not any(x not in DROPPED_TAGS for x in raw):
        return set()
    return set(normalize_tags(raw))


def main() -> None:
    union = load(ROOT / "union")
    bank: dict[str, dict] = {}
    for r in ("content/problems", "content/problems-extended"):
        bank.update(load(ROOT / r))
    by_title: dict[str, str] = {}
    for slug, m in bank.items():
        by_title.setdefault(norm_title(m.get("title", "")), slug)

    pairs: list[tuple[str, str]] = []  # (union slug, our slug)
    missing: list[str] = []
    for uslug, um in union.items():
        if uslug in bank:
            pairs.append((uslug, uslug))
        elif uslug in RENAMES:
            pairs.append((uslug, RENAMES[uslug]))
        elif norm_title(um.get("title", "")) in by_title:
            pairs.append((uslug, by_title[norm_title(um["title"])]))
        else:
            missing.append(uslug)

    tp = fp = fn = 0
    per_tag = defaultdict(lambda: [0, 0, 0])  # tag -> [tp, fp, fn]
    macro_p: list[float] = []
    macro_r: list[float] = []
    exact = 0
    worst: list[tuple[float, str, set, set]] = []
    scored = 0

    for uslug, oslug in sorted(pairs):
        truth = canon(union[uslug].get("tags", []))
        ours = canon(bank[oslug].get("tags", []))
        if not truth:
            continue  # nothing scoreable (e.g. union has no tags at all)
        scored += 1
        hit = truth & ours
        tp += len(hit)
        fp += len(ours - truth)
        fn += len(truth - ours)
        for t in hit:
            per_tag[t][0] += 1
        for t in ours - truth:
            per_tag[t][1] += 1
        for t in truth - ours:
            per_tag[t][2] += 1
        p = len(hit) / len(ours) if ours else 0.0
        r = len(hit) / len(truth)
        macro_p.append(p)
        macro_r.append(r)
        if truth == ours:
            exact += 1
        f1 = 2 * p * r / (p + r) if p + r else 0.0
        worst.append((f1, oslug, truth, ours))

    def f1(p: float, r: float) -> float:
        return 2 * p * r / (p + r) if p + r else 0.0

    P = tp / (tp + fp)
    R = tp / (tp + fn)
    mP = sum(macro_p) / len(macro_p)
    mR = sum(macro_r) / len(macro_r)

    print(f"union problems           : {len(union)}")
    print(f"matched to our bank      : {len(pairs)}  (slug/title/rename join)")
    print(f"not in our bank          : {len(missing)}")
    print(f"scored (non-empty truth) : {scored}")
    print()
    print(f"tag assignments  ours={tp + fp}  truth={tp + fn}  correct={tp}")
    print(f"MICRO   precision {P:.3f}   recall {R:.3f}   F1 {f1(P, R):.3f}")
    print(f"MACRO   precision {mP:.3f}   recall {mR:.3f}   F1 {f1(mP, mR):.3f}")
    print(f"exact set match : {exact}/{scored} ({exact / scored:.1%})")
    print()

    print(f"{'tag':24s} {'truth':>6s} {'ours':>6s} {'tp':>5s} {'prec':>6s} {'rec':>6s} {'F1':>6s}")
    rows = sorted(per_tag.items(), key=lambda kv: -(kv[1][0] + kv[1][2]))
    for tag, (t, f_p, f_n) in rows:
        p = t / (t + f_p) if t + f_p else 0.0
        r = t / (t + f_n) if t + f_n else 0.0
        print(f"{tag:24s} {t + f_n:6d} {t + f_p:6d} {t:5d} {p:6.3f} {r:6.3f} {f1(p, r):6.3f}")
    print()

    miss_c = Counter({k: v[2] for k, v in per_tag.items() if v[2]})
    spur_c = Counter({k: v[1] for k, v in per_tag.items() if v[1]})
    print("most-missed tags (we omit) :", miss_c.most_common(12))
    print("most-spurious tags (we add):", spur_c.most_common(12))
    print()
    worst.sort()
    print("worst 25 problems:")
    for f, slug, truth, ours in worst[:25]:
        print(f"  {f:.2f} {slug:52s} truth={sorted(truth)}  ours={sorted(ours)}")

    if "--missing" in sys.argv:
        print("\nunion slugs absent from the bank:")
        for s in sorted(missing):
            print("  ", s, union[s].get("tags"))


if __name__ == "__main__":
    main()
