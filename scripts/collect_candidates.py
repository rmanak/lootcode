#!/usr/bin/env python3
"""Collect a population of LLM candidate solutions per problem (plan §11.3).

For every problem, ask the local qwen server for several independent solution
attempts at varying temperature / reasoning. Some will be correct, some subtly
wrong — the wrong ones are the realistic stand-in bugs the population-differential
selector will turn into discriminating hidden tests (the canonical stays the sole
oracle; see app/testgen/candidates.py for the trust argument).

This is the slow, network-bound half of the pipeline, so it is a standalone,
**resumable, checkpointed** collector: one JSON per problem under
``testgen_cache/candidates/<slug>.json``. Re-running skips problems already
complete and fills in only missing configs. Concurrency defaults to 2 to match
the server's ``--parallel 2`` slots.

Usage:
    python scripts/collect_candidates.py --limit 3 -v        # smoke test
    python scripts/collect_candidates.py -j 2                # whole bank
    python scripts/collect_candidates.py --filter tree       # a subset
    python scripts/collect_candidates.py two-sum --force -v  # one, regenerate
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app import content  # noqa: E402
from app.testgen.candidates import (  # noqa: E402
    DEFAULT_CONFIGS, THINKING_CONFIGS, Candidate, client, generate_candidate,
)

CACHE_DIR = pathlib.Path(__file__).resolve().parent.parent / "testgen_cache" / "candidates"


def _cache_path(slug: str) -> pathlib.Path:
    return CACHE_DIR / f"{slug}.json"


def _load_cache(slug: str) -> dict | None:
    p = _cache_path(slug)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _write_cache(slug: str, fn: str, cands: list[Candidate]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    data = {
        "slug": slug, "function_name": fn,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "candidates": [c.to_dict() for c in cands],
    }
    tmp = _cache_path(slug).with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    tmp.replace(_cache_path(slug))  # atomic: a crash never leaves a half-file


def _missing_labels(slug: str, want: set[str], force: bool) -> set[str]:
    """Which configured labels still need generating for this slug."""
    if force:
        return set(want)
    cache = _load_cache(slug)
    if not cache:
        return set(want)
    have = {c.get("label") for c in cache.get("candidates", [])}
    return set(want) - have


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slugs", nargs="*", help="only these slugs (default: all)")
    ap.add_argument("--filter", help="only slugs containing this substring")
    ap.add_argument("--limit", type=int, help="cap number of problems (for testing)")
    ap.add_argument("-j", "--jobs", type=int, default=2, help="concurrent requests (server has 2 slots)")
    ap.add_argument("--force", action="store_true", help="regenerate even if cached")
    ap.add_argument("--think", action="store_true",
                    help="also generate the slower reasoning-on configs (top-up)")
    ap.add_argument("--timeout", type=float, default=150.0, help="per-request timeout (s)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    configs = list(DEFAULT_CONFIGS) + (list(THINKING_CONFIGS) if args.think else [])

    all_probs = content.load_all()
    by_slug = {p["slug"]: p for p in all_probs}
    if args.slugs:
        probs = [by_slug[s] for s in args.slugs if s in by_slug]
        for s in args.slugs:
            if s not in by_slug:
                print(f"[ERROR] unknown slug: {s}")
    elif args.filter:
        probs = [p for p in all_probs if args.filter in p["slug"]]
    else:
        probs = all_probs
    if args.limit:
        probs = probs[: args.limit]

    want_labels = {c.label for c in configs}
    cfg_by_label = {c.label: c for c in configs}

    # Build the task list: only (slug, config) pairs not already cached.
    tasks: list[tuple[str, str]] = []
    skipped = 0
    for p in probs:
        miss = _missing_labels(p["slug"], want_labels, args.force)
        if not miss:
            skipped += 1
            continue
        for label in miss:
            tasks.append((p["slug"], label))
    print(f"{len(probs)} problems ({skipped} already complete), "
          f"{len(tasks)} generation tasks, {args.jobs} workers, "
          f"{len(configs)} configs/problem")
    if not tasks:
        print("nothing to do.")
        return 0

    cli = client()
    # Group results by slug; write a slug's file once all its tasks land (merging
    # with any previously-cached candidates so a partial resume is preserved).
    pending: dict[str, set[str]] = {}
    have: dict[str, list[Candidate]] = {}
    for slug, label in tasks:
        pending.setdefault(slug, set()).add(label)
    for slug in pending:
        cache = _load_cache(slug)
        keep = [] if args.force else [
            Candidate(**{k: c.get(k) for k in
                         ("label", "temperature", "thinking", "style", "code",
                          "parse_ok", "error", "elapsed_s", "completion_tokens")})
            for c in (cache.get("candidates", []) if cache else [])
            if c.get("label") in want_labels]
        have[slug] = keep

    t0 = time.time()
    done_probs = 0
    n_ok = n_bad = 0

    def work(task):
        slug, label = task
        return slug, generate_candidate(cli, by_slug[slug], cfg_by_label[label],
                                        timeout=args.timeout)

    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        futs = {ex.submit(work, t): t for t in tasks}
        for fut in as_completed(futs):
            slug, cand = fut.result()
            have[slug].append(cand)
            if cand.parse_ok:
                n_ok += 1
            else:
                n_bad += 1
            if args.verbose:
                tag = "ok " if cand.parse_ok else "BAD"
                err = f" err={cand.error}" if cand.error else ""
                print(f"    [{tag}] {slug}:{cand.label} "
                      f"({cand.elapsed_s:.1f}s, {cand.completion_tokens}tok){err}")
            pending[slug].discard(cand.label)
            if not pending[slug]:
                _write_cache(slug, by_slug[slug]["function_name"], have[slug])
                done_probs += 1
                rate = (time.time() - t0) / max(1, done_probs)
                remaining = (len(pending) - done_probs) * rate
                if not args.verbose or done_probs % 10 == 0:
                    print(f"[{done_probs}/{len(pending)}] {slug} "
                          f"({len(have[slug])} cands) "
                          f"~{rate:.1f}s/prob, ETA {remaining/60:.0f}m")

    dt = time.time() - t0
    print(f"\nDone: {done_probs} problems written, {n_ok} parseable / "
          f"{n_ok + n_bad} attempts, {dt/60:.1f}m total "
          f"({dt/max(1,done_probs):.1f}s/problem)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
