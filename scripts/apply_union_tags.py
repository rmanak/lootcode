#!/usr/bin/env python3
"""Adopt `union/` tags as ground truth for the problems we share with it.

Three passes over the on-disk bank (both content roots):

1. **Matched problems** — for every problem that also exists in `union/`, replace
   our ``tags`` with union's, mapped through ``app.tags.normalize_tags``. Union
   is the ground truth, so its set wins outright. A problem whose union tags
   normalize to *nothing* (the 13 SQL-derived ones, whose only union tag is
   ``database``) keeps ours — we re-authored those as Python array problems and
   union's tagging no longer describes them.

2. **Every problem** — re-normalize, so the vocabulary changes that came with
   this migration (``hash-set`` -> ``hash-table``, the stray ``interval``) land on
   the ~473 problems union has never heard of too.

3. **Unmatched problems that ``scripts/build_bank.py`` authored** — that file
   still holds the ``topics`` the author originally wrote, *before* the old
   aliases folded them away (``segment-tree`` -> ``binary-indexed-tree``,
   ``ordered-set`` -> ``binary-search-tree``, ``dijkstra``/``topological-sort`` ->
   ``graph``). Re-running those literals through the new normalizer recovers the
   recorded intent for problems union can't speak to. Only applied where it
   restores a tag this migration promoted — never to overwrite later hand edits.

``scripts/build_bank.py`` hard-codes ``topics`` for 231 problems and would revert
this migration on its next run, so its literals are rewritten in step 4.

The union join is not pure slug equality: 17 problems live in our bank under a
different slug and/or title. `RENAMES` is the hand-verified table for the ones
where both drifted; the rest fall out of a normalized-title match.

    python scripts/apply_union_tags.py            # report, write nothing
    python scripts/apply_union_tags.py --apply    # ...then write
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.tags import DROPPED_TAGS, normalize_tags  # noqa: E402

UNION_DIR = ROOT / "union"
CONTENT_ROOTS = (ROOT / "content" / "problems", ROOT / "content" / "problems-extended")
BUILD_BANK = ROOT / "scripts" / "build_bank.py"

# union slug -> our slug, for problems whose slug *and* title both drifted.
# Each one was verified by reading both statements.
RENAMES = {
    "alien-dictionary": "alien-dictionary-order",
    "convert-sorted-array-to-binary-search-tree": "sorted-array-to-bst",
    "design-hit-counter": "hit-counter",
    "design-in-memory-file-system": "in-memory-file-system",
    "design-search-autocomplete-system": "autocomplete-top-k",
    "find-eventual-safe-states": "eventual-safe-states",
    "find-median-from-data-stream": "median-from-data-stream",
    "find-the-duplicate-number": "find-duplicate-number",
    "kth-largest-element-in-an-array": "kth-largest-element",
    "maximum-profit-in-job-scheduling": "maximum-profit-job-scheduling",
    "meeting-rooms-ii": "meeting-rooms-required",
    "search-insert-position": "binary-search-insert-position",
    "web-crawler": "web-crawler-same-host",
}


def norm_title(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (title or "").lower()).strip()


def load_metas(root: Path) -> dict[str, tuple[Path, dict]]:
    out: dict[str, tuple[Path, dict]] = {}
    for meta in sorted(root.glob("*/meta.json")):
        out[meta.parent.name] = (meta, json.loads(meta.read_text(encoding="utf-8")))
    return out


def join() -> tuple[dict[str, str], list[str]]:
    """union slug -> our slug, plus the union slugs with no counterpart."""
    union = load_metas(UNION_DIR)
    bank: dict[str, tuple[Path, dict]] = {}
    for root in CONTENT_ROOTS:
        bank.update(load_metas(root))
    by_title: dict[str, str] = {}
    for slug, (_, meta) in bank.items():
        by_title.setdefault(norm_title(meta.get("title", "")), slug)

    pairs: dict[str, str] = {}
    missing: list[str] = []
    for uslug, (_, umeta) in union.items():
        if uslug in bank:
            pairs[uslug] = uslug
        elif uslug in RENAMES:
            target = RENAMES[uslug]
            if target not in bank:
                raise SystemExit(f"RENAMES points at a slug that is gone: {target}")
            pairs[uslug] = target
        elif norm_title(umeta.get("title", "")) in by_title:
            pairs[uslug] = by_title[norm_title(umeta["title"])]
        else:
            missing.append(uslug)
    return pairs, missing


# Tags this migration split out of a roll-up. Step 3 fires only for these: any
# other build_bank/disk disagreement is a later hand edit we must not clobber.
PROMOTED = frozenset({
    "segment-tree", "ordered-set", "topological-sort", "shortest-path",
    "number-theory", "geometry",
})

ADD_CALL = re.compile(
    r'add\("([a-z0-9-]+)",\s*"[^"]*",\s*"[a-z]+",\s*(\[[^\]]*\])', re.S)


def build_bank_topics() -> dict[str, list[str]]:
    """slug -> the `topics` literal build_bank.py passes to `add(...)`."""
    return {m.group(1): json.loads(m.group(2))
            for m in ADD_CALL.finditer(BUILD_BANK.read_text(encoding="utf-8"))}


def union_says_something(umeta: dict) -> bool:
    """Does union carry a tag that survives our vocabulary?

    ``normalize_tags`` can't answer this: it never returns empty, falling back to
    ``["math"]``. So a problem whose only union tag is ``database`` would come
    back looking like a math problem. Check the raw list against the fold rules
    first, and treat "nothing survives" as "union has no opinion — keep ours".
    """
    raw = [t.strip().lower() for t in (umeta.get("tags") or []) if t and t.strip()]
    return any(t not in DROPPED_TAGS for t in raw)


LINE_LENGTH = 88  # pyproject [tool.ruff] line-length; build_bank.py is linted


def render_list(tags: list[str], start_col: int, indent: str) -> str:
    """A Python list literal that fits in the line budget, wrapping if it can't."""
    flat = json.dumps(tags)
    if start_col + len(flat) <= LINE_LENGTH:
        return flat
    lines, cur = [], "["
    for i, tag in enumerate(tags):
        piece = json.dumps(tag) + ("," if i < len(tags) - 1 else "]")
        budget = LINE_LENGTH - (start_col if not lines else len(indent))
        if cur != "[" and len(cur) + 1 + len(piece) > budget:
            lines.append(cur)
            cur = indent + piece
        else:
            cur += (" " if cur != "[" else "") + piece
    lines.append(cur)
    return "\n".join(lines)


def rewrite_build_bank(changed: dict[str, list[str]], apply: bool) -> int:
    """Update the hard-coded `topics` list in each affected `add(...)` call.

    build_bank.py writes straight into content/problems/, so leaving its literals
    stale would mean the next run silently reverts this migration.
    """
    text = BUILD_BANK.read_text(encoding="utf-8")
    hits = 0
    for slug, tags in changed.items():
        # add("<slug>", "<title>", "<difficulty>", [<topics>], ...
        pat = re.compile(
            r'(add\("' + re.escape(slug) + r'",\s*"[^"]*",\s*"[a-z]+",\s*)\[[^\]]*\]',
            re.S,
        )

        def repl(m: re.Match[str], tags: list[str] = tags) -> str:
            prefix = m.group(1)
            last = prefix[prefix.rfind("\n") + 1:]
            indent = " " * (len(last) - len(last.lstrip()) or 4)
            return prefix + render_list(tags, len(last), indent)

        text, n = pat.subn(repl, text)
        hits += n
    if apply and hits:
        BUILD_BANK.write_text(text, encoding="utf-8")
    return hits


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="write the changes")
    ap.add_argument("-v", "--verbose", action="store_true", help="print every change")
    args = ap.parse_args()

    union = load_metas(UNION_DIR)
    pairs, missing = join()
    ours_to_union = {o: u for u, o in pairs.items()}

    bb_topics = build_bank_topics()
    adopted = renormalized = recovered = kept_empty = 0
    added: Counter[str] = Counter()
    removed: Counter[str] = Counter()
    changed_slugs: dict[str, list[str]] = {}

    for root in CONTENT_ROOTS:
        for slug, (path, meta) in load_metas(root).items():
            before = list(meta.get("tags") or [])
            uslug = ours_to_union.get(slug)
            source = "renormalize"
            if uslug is not None and union_says_something(union[uslug][1]):
                after = normalize_tags(union[uslug][1].get("tags") or [])
                source = "union"
            else:
                kept_empty += uslug is not None
                after = normalize_tags(before)
                # Step 3: recover intent the old aliases folded away.
                intent = bb_topics.get(slug)
                if intent is not None:
                    want = normalize_tags(intent)
                    if PROMOTED & (set(want) - set(after)):
                        after = want
                        source = "build_bank"

            if after == before:
                continue
            if source == "union":
                adopted += 1
            elif source == "build_bank":
                recovered += 1
            else:
                renormalized += 1
            added.update(set(after) - set(before))
            removed.update(set(before) - set(after))
            changed_slugs[slug] = after
            if args.verbose:
                print(f"  {slug:52s} {before} -> {after}")
            if args.apply:
                meta["tags"] = after
                path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    bb = rewrite_build_bank(changed_slugs, args.apply)

    verb = "wrote" if args.apply else "would change"
    print(f"union problems              : {len(union)}")
    print(f"matched to the bank         : {len(pairs)}   (not in bank: {len(missing)})")
    print(f"union tags unusable, kept ours: {kept_empty}")
    print()
    print(f"{verb} {len(changed_slugs)} problems ({adopted} adopting union tags, "
          f"{recovered} recovering build_bank intent, {renormalized} re-normalized only)")
    print(f"  +{sum(added.values())} tags   -{sum(removed.values())} tags")
    print(f"  build_bank.py topics rewritten: {bb}")
    print()
    print("most added  :", added.most_common(12))
    print("most removed:", removed.most_common(12))
    if not args.apply:
        print("\n(dry run — pass --apply to write)")


if __name__ == "__main__":
    main()
