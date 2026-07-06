"""Generate progressive hints for every problem and write them into meta.json.

For each `content/problems/<slug>/`, this reads `problem.md` (the statement),
asks the local LLM for up to 3 progressive, non-spoiling hints via
`app.llm.hint_generator.generate_hints`, and inserts a `hints` array into that
problem's `meta.json` (right after `tags`, matching `write_problem_files`).

It is:
- **Surgical** — only the `hints` key is added; tests, starters, solutions and
  every other meta field are left byte-for-byte alone (no repo-wide churn).
- **Parallel** — requests fan out over a thread pool (the llama.cpp server here
  runs 4 slots, so `--workers 4` is the sweet spot). Generation is HTTP-bound,
  so threads are fine.
- **Resumable / idempotent** — problems that already have hints are skipped
  unless `--force`, and each meta.json is written the moment its hints arrive,
  so an interrupted run loses nothing.

meta.json is the durable source of truth; the DB re-seeds from it. After this
runs, reseed (`python scripts/seed.py`) or restart the app to pick up the hints.

Usage (from the project root):
    python scripts/generate_hints.py                  # all problems missing hints
    python scripts/generate_hints.py --workers 4      # match the server's slots
    python scripts/generate_hints.py --slug happy-number --force
    python scripts/generate_hints.py --limit 10 --dry-run
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402
from app.content import MAX_HINTS, normalize_hints  # noqa: E402
from app.llm.hint_generator import LLM_MODEL, LLM_SERVER_URL, generate_hints  # noqa: E402


def _iter_problem_dirs(content_dir: pathlib.Path):
    for child in sorted(content_dir.iterdir()):
        if child.is_dir() and (child / "meta.json").exists():
            yield child


def _meta_with_hints(meta: dict, hints: list[str]) -> dict:
    """Return a copy of `meta` with `hints` placed just after `tags`.

    Preserves the existing key order (and any extra fields) so the on-disk diff
    is exactly the added block. Falls back to appending if there is no `tags` key.
    """
    out: dict = {}
    placed = False
    for key, value in meta.items():
        if key == "hints":  # drop any stale value; we re-place it
            continue
        out[key] = value
        if key == "tags":
            out["hints"] = hints
            placed = True
    if not placed:
        out["hints"] = hints
    return out


def _write_hints(dir_path: pathlib.Path, hints: list[str]) -> None:
    meta_path = dir_path / "meta.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    updated = _meta_with_hints(meta, hints)
    # indent=2 + trailing newline matches app/content.write_problem_files exactly.
    meta_path.write_text(json.dumps(updated, indent=2) + "\n", encoding="utf-8")


def _preflight(base_url: str) -> bool:
    """Cheap reachability check so we fail fast instead of 700x when the server is down."""
    url = f"{base_url.rstrip('/')}/v1/models"
    try:
        with urllib.request.urlopen(url, timeout=5) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError):
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workers", type=int, default=4,
                    help="parallel requests (match the server's slot count; default 4)")
    ap.add_argument("--slug", action="append", default=[],
                    help="only this slug (repeatable); default = all problems")
    ap.add_argument("--limit", type=int, default=0,
                    help="cap how many problems to process (0 = no cap)")
    ap.add_argument("--force", action="store_true",
                    help="regenerate even for problems that already have hints")
    ap.add_argument("--max-hints", type=int, default=MAX_HINTS,
                    help=f"max hints per problem (1..{MAX_HINTS}, default {MAX_HINTS})")
    ap.add_argument("--thinking", action="store_true",
                    help="let the model 'think' first (higher quality, ~10x slower)")
    ap.add_argument("--base-url", default=LLM_SERVER_URL,
                    help=f"LLM server base URL (default {LLM_SERVER_URL})")
    ap.add_argument("--model", default=os.environ.get("LLM_MODEL") or LLM_MODEL,
                    help="model name to request")
    ap.add_argument("--dry-run", action="store_true",
                    help="generate and print hints but do NOT write meta.json")
    args = ap.parse_args()

    content_dir = settings.CONTENT_DIR
    wanted = set(args.slug)

    # Decide the worklist: skip problems that already have hints (unless --force).
    todo: list[pathlib.Path] = []
    skipped = 0
    for d in _iter_problem_dirs(content_dir):
        if wanted and d.name not in wanted:
            continue
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        statement = (d / "problem.md").read_text(encoding="utf-8") if (d / "problem.md").exists() else ""
        if not statement.strip():
            print(f"  - {d.name}: no statement (problem.md missing/empty) — skipped")
            skipped += 1
            continue
        if normalize_hints(meta.get("hints")) and not args.force:
            skipped += 1
            continue
        todo.append(d)

    if args.limit and args.limit > 0:
        todo = todo[:args.limit]

    if not todo:
        print(f"Nothing to do ({skipped} already had hints / were skipped).")
        return 0

    if not _preflight(args.base_url):
        print(f"ERROR: LLM server not reachable at {args.base_url} "
              f"(checked {args.base_url.rstrip('/')}/v1/models). Is it running?")
        return 1

    mode = "thinking" if args.thinking else "fast"
    print(f"Generating hints for {len(todo)} problem(s) "
          f"[{args.workers} workers, model={args.model}, {mode} mode]"
          f"{' — DRY RUN' if args.dry_run else ''}. "
          f"{skipped} already had hints.\n")

    def work(d: pathlib.Path) -> tuple[pathlib.Path, list[str]]:
        statement = (d / "problem.md").read_text(encoding="utf-8")
        hints = generate_hints(
            statement, max_hints=args.max_hints, base_url=args.base_url,
            model=args.model, thinking=args.thinking,
        )
        return d, hints

    done = failed = empty = 0
    total = len(todo)
    try:
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {pool.submit(work, d): d for d in todo}
            for i, fut in enumerate(as_completed(futures), 1):
                d = futures[fut]
                try:
                    _, hints = fut.result()
                except Exception as e:  # noqa: BLE001 - one problem's failure isn't fatal
                    failed += 1
                    print(f"[{i}/{total}] FAIL {d.name}: {type(e).__name__}: {e}")
                    continue
                if not hints:
                    empty += 1
                    print(f"[{i}/{total}] WARN {d.name}: model returned no usable hints")
                    continue
                if not args.dry_run:
                    _write_hints(d, hints)
                done += 1
                print(f"[{i}/{total}] OK   {d.name} ({len(hints)} hints)"
                      + ("" if not args.dry_run else "  " + " | ".join(hints)))
    except KeyboardInterrupt:
        print("\nInterrupted — hints written so far are saved; re-run to resume.")

    print(f"\nDone. wrote={done} failed={failed} empty={empty} "
          f"skipped_existing={skipped}"
          + ("  (dry run: nothing written)" if args.dry_run else ""))
    if done and not args.dry_run:
        print("Reseed to load hints into the DB:  python scripts/seed.py")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
