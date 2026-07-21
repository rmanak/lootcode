#!/usr/bin/env python3
"""Find potential duplicate problems by fuzzy-matching their *slugs* only.

The heuristic: two problems are likely duplicates when their slugs are very
similar strings -- in particular when one slug is a substring of the other, or
when they share a long common substring / most of their word-tokens.

This looks at nothing but the slug (the problem directory name) under the
content roots, so it is cheap and content-agnostic: a fast first-pass triage
that a human (or a follow-up content check) can confirm.

Usage:
    python scripts/find_duplicate_slugs.py                 # write duplicate_slugs.txt
    python scripts/find_duplicate_slugs.py -o dupes.txt    # custom output
    python scripts/find_duplicate_slugs.py --min-ratio 0.8 # stricter
    python scripts/find_duplicate_slugs.py --content-dir content/problems

By default it scans both content roots (content/problems and
content/problems-extended). Output is a ranked, human-readable text report.
"""
from __future__ import annotations

import argparse
import sys
from difflib import SequenceMatcher
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOTS = [
    REPO_ROOT / "content" / "problems",
    REPO_ROOT / "content" / "problems-extended",
]


def collect_slugs(roots: list[Path]) -> dict[str, list[str]]:
    """Return {slug: [root_name, ...]} for every problem directory found."""
    slugs: dict[str, list[str]] = {}
    for root in roots:
        if not root.is_dir():
            continue
        for child in sorted(root.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            slugs.setdefault(child.name, []).append(root.name)
    return slugs


def longest_common_substring_len(a: str, b: str) -> int:
    """Length of the longest contiguous substring shared by a and b."""
    match = SequenceMatcher(None, a, b, autojunk=False).find_longest_match(
        0, len(a), 0, len(b)
    )
    return match.size


def tokens(slug: str) -> set[str]:
    return {t for t in slug.split("-") if t}


# Roman-numeral tier tokens (i..x) used as LeetCode-style variant suffixes.
_ROMAN = {"i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}


def variant_base(slug: str) -> str:
    """Slug with a trailing variant-tier token removed (e.g. '-ii', '-2').

    'combination-sum-iii' -> 'combination-sum'; 'my-calendar' -> 'my-calendar'.
    Only a single trailing roman-numeral or bare-integer token is stripped.
    """
    parts = slug.split("-")
    if len(parts) > 1 and (parts[-1] in _ROMAN or parts[-1].isdigit()):
        return "-".join(parts[:-1])
    return slug


def is_variant_pair(a: str, b: str) -> bool:
    """True when a and b differ only by a numeral tier (e.g. foo vs foo-ii).

    These are almost always follow-up / harder variants of the same base
    problem rather than duplicates, so the finder skips them.
    """
    if a == b:
        return False
    return variant_base(a) == variant_base(b)


def score_pair(a: str, b: str, include_variants: bool = False) -> dict | None:
    """Compute similarity signals for a slug pair; None if clearly unrelated.

    Returns a dict of metrics plus a combined ``score`` and ``reasons`` list.
    Numeral-tier variant pairs (foo vs foo-ii) are skipped unless
    ``include_variants`` is set.
    """
    if a == b:
        return None
    if not include_variants and is_variant_pair(a, b):
        return None

    ratio = SequenceMatcher(None, a, b, autojunk=False).ratio()

    lcs = longest_common_substring_len(a, b)
    shorter = min(len(a), len(b))
    lcs_ratio = lcs / shorter if shorter else 0.0

    ta, tb = tokens(a), tokens(b)
    inter = ta & tb
    union = ta | tb
    jaccard = len(inter) / len(union) if union else 0.0

    # substring relationships
    raw_substring = a in b or b in a
    token_subset = bool(ta) and bool(tb) and (ta <= tb or tb <= ta)

    reasons: list[str] = []
    if raw_substring:
        reasons.append("substring")
    if token_subset:
        reasons.append("token-subset")
    if lcs_ratio >= 0.70:
        reasons.append(f"common-substr={lcs}({lcs_ratio:.0%})")
    if jaccard >= 0.60:
        reasons.append(f"token-jaccard={jaccard:.0%}")
    if ratio >= 0.75:
        reasons.append(f"ratio={ratio:.0%}")

    if not reasons:
        return None

    # Combined score. A substring / token-subset relationship is *flagged*
    # (as the user asked) but does not by itself pin the score to ~1.0 --
    # otherwise a short generic slug ("binary-search") that happens to sit
    # inside a dozen unrelated slugs ("validate-binary-search-tree") would
    # drown out true duplicates. Rank by genuine string closeness instead,
    # so near-identical pairs (roman-numeral / "design-" variants) float up.
    score = 0.60 * ratio + 0.20 * lcs_ratio + 0.20 * jaccard
    if token_subset or raw_substring:
        # small bonus, scaled by how much of the longer slug the shorter one
        # actually covers (length similarity) -- generic substrings barely move.
        length_cover = shorter / max(len(a), len(b))
        score = min(1.0, score + 0.15 * length_cover)
    return {
        "a": a,
        "b": b,
        "score": score,
        "ratio": ratio,
        "lcs": lcs,
        "lcs_ratio": lcs_ratio,
        "jaccard": jaccard,
        "reasons": reasons,
    }


def find_candidates(
    slugs: list[str],
    min_ratio: float,
    min_lcs_ratio: float,
    min_jaccard: float,
    include_variants: bool = False,
) -> list[dict]:
    """Blocked pairwise comparison: only compare slugs that share a token."""
    # Inverted index token -> slug indices, to avoid comparing every pair.
    index: dict[str, list[int]] = {}
    for i, slug in enumerate(slugs):
        for tok in tokens(slug):
            index.setdefault(tok, []).append(i)

    seen: set[tuple[int, int]] = set()
    results: list[dict] = []
    for members in index.values():
        for x in range(len(members)):
            for y in range(x + 1, len(members)):
                i, j = members[x], members[y]
                key = (i, j) if i < j else (j, i)
                if key in seen:
                    continue
                seen.add(key)
                res = score_pair(slugs[i], slugs[j], include_variants)
                if res is None:
                    continue
                # Honor CLI thresholds (score_pair uses defaults for reasons,
                # but the combined score gate is applied here).
                if (
                    res["ratio"] >= min_ratio
                    or res["lcs_ratio"] >= min_lcs_ratio
                    or res["jaccard"] >= min_jaccard
                    or "substring" in res["reasons"]
                    or "token-subset" in res["reasons"]
                ):
                    results.append(res)

    results.sort(key=lambda r: (-r["score"], r["a"], r["b"]))
    return results


def render(results: list[dict], n_slugs: int, roots: list[Path]) -> str:
    lines: list[str] = []
    lines.append("# Potential duplicate slugs (fuzzy slug matching only)")
    lines.append(f"# scanned roots: {', '.join(str(r) for r in roots)}")
    lines.append(f"# slugs: {n_slugs}   candidate pairs: {len(results)}")
    lines.append("# columns: score  slug_a  <->  slug_b  [reasons]")
    lines.append("")
    for r in results:
        lines.append(
            f"{r['score']:.2f}  {r['a']}  <->  {r['b']}  [{', '.join(r['reasons'])}]"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--content-dir",
        action="append",
        type=Path,
        help="content root to scan (repeatable); default: both problem roots",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=REPO_ROOT / "duplicate_slugs.txt",
        help="output text file (default: duplicate_slugs.txt at repo root)",
    )
    p.add_argument("--min-ratio", type=float, default=0.75,
                   help="SequenceMatcher ratio threshold (default 0.75)")
    p.add_argument("--min-lcs-ratio", type=float, default=0.70,
                   help="longest-common-substring / shorter-len threshold (0.70)")
    p.add_argument("--min-jaccard", type=float, default=0.60,
                   help="token Jaccard threshold (default 0.60)")
    p.add_argument("--include-variants", action="store_true",
                   help="keep numeral-tier variant pairs (foo vs foo-ii), "
                        "which are excluded by default as follow-up problems")
    args = p.parse_args()

    roots = args.content_dir or DEFAULT_ROOTS
    slug_map = collect_slugs(roots)
    if not slug_map:
        print(f"No slugs found under: {', '.join(str(r) for r in roots)}",
              file=sys.stderr)
        return 1

    slugs = sorted(slug_map)
    results = find_candidates(
        slugs, args.min_ratio, args.min_lcs_ratio, args.min_jaccard,
        args.include_variants,
    )

    report = render(results, len(slugs), roots)
    args.output.write_text(report)
    print(f"Scanned {len(slugs)} slugs; wrote {len(results)} candidate pairs "
          f"to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
