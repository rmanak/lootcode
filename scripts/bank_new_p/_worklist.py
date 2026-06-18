"""Worklist for the new_p.txt import — durable, self-healing across context resets.

`pending()` = NEW unique LeetCode entries from new_p.txt, cleaned, that are not yet
in the bank and not yet written into any `batch_*.py`. The set of slugs already in
the batch files IS the done-marker, so there is no separate state file to drift.

CLI:
    python -m scripts.bank_new_p._worklist            # summary counts
    python -m scripts.bank_new_p._worklist next 20    # dump next 20 pending (slug + statement)
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
import unicodedata

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = ROOT / "new_p.txt"
PKG_DIR = pathlib.Path(__file__).resolve().parent

_ROMAN = {"ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"}


def title_from_slug(slug: str) -> str:
    out = []
    for w in slug.split("-"):
        if w in _ROMAN:
            out.append(w.upper())
        elif w.isdigit():
            out.append(w)
        else:
            out.append(w[:1].upper() + w[1:])
    return " ".join(out)


def _clean(text: str) -> str:
    text = text.replace("\xa0", " ").replace("​", "")
    text = unicodedata.normalize("NFKC", text)
    return text.strip()


def parse_all() -> list[dict]:
    raw = SRC.read_text(encoding="utf-8", errors="replace")
    out = []
    for block in raw.split("=" * 80):
        if not block.strip():
            continue
        lines = block.splitlines()
        url, body_start = "", 0
        for i, ln in enumerate(lines):
            s = ln.strip()
            if s.lower().startswith("# url:"):
                url = s.split(":", 1)[1].strip()
            elif s.lower().startswith("# problem:"):
                body_start = i + 1
                break
        m = re.search(r"/problems/([a-z0-9-]+)", url)
        slug = m.group(1) if m else ""
        out.append({
            "url": url,
            "slug": slug,
            "title": title_from_slug(slug),
            "statement": _clean("\n".join(lines[body_start:])),
        })
    return out


def bank_slugs() -> set[str]:
    dirs = {p.name for p in (ROOT / "content" / "problems").iterdir() if p.is_dir()}
    bank = set(re.findall(r'add\(\s*"([a-z0-9-]+)"', (ROOT / "scripts" / "build_bank.py").read_text()))
    return dirs | bank


def batched_slugs() -> set[str]:
    done = set()
    for f in PKG_DIR.glob("batch_*.py"):
        done |= set(re.findall(r'add\(\s*"([a-z0-9-]+)"', f.read_text()))
    return done


def skip_slugs() -> set[str]:
    from scripts.bank_new_p._skips import SKIP
    return set(SKIP)


def pending() -> list[dict]:
    done = bank_slugs() | batched_slugs() | skip_slugs()
    seen, out = set(), []
    for e in parse_all():
        s = e["slug"]
        if not s or s in seen or s in done:
            continue
        seen.add(s)
        out.append(e)
    return out


if __name__ == "__main__":
    allp = parse_all()
    pend = pending()
    if len(sys.argv) >= 2 and sys.argv[1] == "next":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 20
        print(json.dumps(pend[:n], indent=1))
    else:
        print(f"total parsed:       {len(allp)}")
        print(f"in bank:            {len(bank_slugs())}")
        print(f"already in batches: {len(batched_slugs())}")
        print(f"skipped (dup/unfit):{len(skip_slugs())}")
        print(f"PENDING:            {len(pend)}")
