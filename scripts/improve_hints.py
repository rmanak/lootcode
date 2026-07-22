"""Audit and improve problem hints with a generate -> judge -> regenerate loop.

The bank's hints were generated one-shot with no quality gate, so a large fraction
of final-tier hints give away the whole solution (the exact recurrence / algorithm)
while a minority are too vague. This tool adds the missing gate. It never invents an
answer of its own — the canonical solution is the only yardstick — and it leaves
good hints untouched.

Two roles, both played by the local Qwen model (see app/llm/hint_generator.py):
  * generator  — writes hints from the statement only (no solution => no transcription)
  * judge      — grades each hint against the canonical solution as `ok` / `reveals`
                 / `vague`, and says which tiers to regenerate (thinking ON)

Subcommands
-----------
  audit      Grade existing hints across the bank; write a report; change nothing.
             This is the triage pass -> .hints/audit.json.
  fix        Regenerate the flagged hint sets via the verified loop and write them
             back to meta.json. DRY-RUN by default; pass --apply to write. Only
             problems that come out strictly better than before are overwritten.
  calibrate  Sanity-check the judge against app/llm/hint_exemplars.json (gold sets
             must grade `ok`; known leaks must be caught). Validates the rubric.
  apply-report  Write the reviewed hints straight from a fix dry-run report
             (.hints/fix-dry.json) into meta.json — the exact sets you previewed,
             no regeneration, no LLM calls. DRY-RUN by default; --apply to write.

Typical flow (from the project root; server = local Qwen on :8080):
    python scripts/improve_hints.py calibrate                     # trust the judge
    python scripts/improve_hints.py audit                         # triage all 741
    python scripts/improve_hints.py fix --from-report --dry-run   # preview fixes
    python scripts/improve_hints.py fix --from-report --apply     # write them
    python scripts/seed.py                                        # load into the DB

Resumability
------------
Every slug is an independent task. `audit` and `fix` checkpoint each slug to a
crash-safe append-only log (`.hints/<cmd>.progress.jsonl`) the instant it finishes:
the line is flushed and ``fsync``'d before the next slug is handed out, so a hard
kill (SIGKILL, power loss) loses only the slugs still in flight (at most --workers
of them) — everything finished is durable. Re-running the same command skips the
completed slugs and picks up where it stopped; `--restart` forces a clean run. The
log is deleted once the whole pass finishes. For `fix --apply`, meta.json is also
the durable source of truth: writes are surgical (only the `hints` block changes)
and happen the moment new hints are accepted.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))  # reuse generate_hints' surgical writer

from app.config import settings  # noqa: E402
from app.content import MAX_HINTS, normalize_hints  # noqa: E402
from app.llm.hint_generator import (  # noqa: E402
    LLM_SERVER_URL, generate_hints_verified, judge_hints, leak_flags,
)
from generate_hints import _meta_with_hints, _preflight, _write_hints  # noqa: E402,F401

DEFAULT_MODEL = os.environ.get("LLM_MODEL") or "qwen36"
REPORT_PATH = ROOT / ".hints" / "audit.json"
EXEMPLARS_PATH = ROOT / "app" / "llm" / "hint_exemplars.json"


# --------------------------------------------------------------------------- #
# Small helpers
# --------------------------------------------------------------------------- #
def _iter_problem_dirs(content_dirs):
    """Yield every `<root>/<slug>/` dir with a meta.json, across all content roots."""
    for root in content_dirs:
        if not root.exists():
            continue
        for child in sorted(root.iterdir()):
            if child.is_dir() and (child / "meta.json").exists():
                yield child


def _load(dir_path: pathlib.Path):
    meta = json.loads((dir_path / "meta.json").read_text(encoding="utf-8"))
    slug = meta.get("slug", dir_path.name)
    stmt_p = dir_path / "problem.md"
    statement = stmt_p.read_text(encoding="utf-8") if stmt_p.exists() else ""
    sol_p = dir_path / "solution" / "solution.py"
    solution = sol_p.read_text(encoding="utf-8") if sol_p.exists() else ""
    hints = normalize_hints(meta.get("hints"))
    return slug, statement, solution, hints


def _select(dirs, slugs, substr, limit):
    wanted = set(slugs)
    out = []
    for d in dirs:
        if wanted and d.name not in wanted:
            continue
        if substr and substr not in d.name:
            continue
        out.append(d)
    if limit and limit > 0:
        out = out[:limit]
    return out


class _C:
    """Tiny ANSI colorizer (no-op when disabled / not a tty)."""
    def __init__(self, on): self.on = on
    def _w(self, s, code): return f"\033[{code}m{s}\033[0m" if self.on else s
    def red(self, s): return self._w(s, "31")
    def yellow(self, s): return self._w(s, "33")
    def green(self, s): return self._w(s, "32")
    def dim(self, s): return self._w(s, "2")
    def bold(self, s): return self._w(s, "1")


def _classify(flags: dict, verdicts: list) -> str:
    labels = {v["tier"]: v["label"] for v in verdicts}
    flagged = sorted(set(flags) | {t for t, l in labels.items() if l != "ok"})
    if not flagged:
        return "clean"
    if flags or any(labels.get(t) == "reveals" for t in flagged):
        return "leak"
    return "vague"


# --------------------------------------------------------------------------- #
# Crash-safe per-slug checkpoint (resumable runs)
# --------------------------------------------------------------------------- #
class _Checkpoint:
    """Append-only per-slug progress log so audit/fix runs are resumable.

    Each slug is an independent task; when it finishes, its record is appended as
    one JSON line, then flushed and ``fsync``'d under a lock before the next slug
    is handed out. A hard kill (SIGKILL, power loss) therefore loses only the slugs
    still in flight — at most ``--workers`` of them — while every completed slug is
    durable on disk. On restart, :attr:`done` maps the already-finished slugs to
    their records so the caller skips them. The first line is a ``{"_meta": ...}``
    header; on resume the caller compares it and refuses to mix incompatible runs
    unless ``--restart`` is passed. Call :meth:`finalize` when the whole pass
    completes to delete the log.
    """

    def __init__(self, path: pathlib.Path, meta: dict):
        self.path = path
        self.meta = meta
        self.done: dict[str, dict] = {}
        self.prior_meta: dict | None = None
        self._lock = threading.Lock()
        self._f = None

    def load(self) -> "_Checkpoint":
        if self.path.exists():
            for line in self.path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue  # a torn final line from a hard kill — drop it
                if "_meta" in obj:
                    self.prior_meta = obj["_meta"]
                elif obj.get("slug"):
                    self.done[obj["slug"]] = obj
        return self

    @property
    def resuming(self) -> bool:
        return bool(self.done)

    def incompatible(self) -> str | None:
        """Human-readable reason a prior log can't be resumed into this run, else None."""
        if self.prior_meta is None:
            return None
        diff = [k for k in ("cmd", "model", "no_judge", "apply")
                if self.prior_meta.get(k) != self.meta.get(k)]
        return ", ".join(diff) if diff else None

    def reset(self) -> None:
        self.done.clear()
        self.prior_meta = None
        self.path.unlink(missing_ok=True)

    def open(self) -> "_Checkpoint":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fresh = not self.path.exists()
        self._f = self.path.open("a", encoding="utf-8")
        if fresh:
            self._write({"_meta": self.meta})
        return self

    def _write(self, obj: dict) -> None:
        self._f.write(json.dumps(obj) + "\n")
        self._f.flush()
        os.fsync(self._f.fileno())

    def record(self, rec: dict) -> None:
        """Durably append one finished slug's record (thread-safe)."""
        with self._lock:
            self._write(rec)
            self.done[rec["slug"]] = rec

    def close(self) -> None:
        if self._f:
            self._f.close()
            self._f = None

    def finalize(self) -> None:
        self.close()
        self.path.unlink(missing_ok=True)


def _progress_path(name: str) -> pathlib.Path:
    return REPORT_PATH.parent / f"{name}.progress.jsonl"


def _slugs_from_file(path: pathlib.Path) -> list[str]:
    """One slug per line; blank lines and `#` comments ignored."""
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def _slugs_from_dir(path: pathlib.Path) -> list[str]:
    """Immediate child dirs of `path` that look like problems (have meta.json)."""
    return sorted(c.name for c in path.iterdir()
                  if c.is_dir() and (c / "meta.json").exists())


def _resolve_slugs(args) -> None:
    """Merge --slugs / --slugs-file / --slugs-dir into args.slug (in place).

    All slug sources are additive and combine with any --slug flags. Downstream
    selection (_select / apply-report / calibrate) already keys off args.slug, so
    folding everything into it keeps one selection path.
    """
    extra: list[str] = []
    for csv in getattr(args, "slugs", None) or []:
        extra += [s.strip() for s in csv.split(",") if s.strip()]
    for f in getattr(args, "slugs_file", None) or []:
        p = pathlib.Path(f)
        if not p.exists():
            print(f"ERROR: --slugs-file not found: {p}")
            raise SystemExit(2)
        extra += _slugs_from_file(p)
    for dpath in getattr(args, "slugs_dir", None) or []:
        p = pathlib.Path(dpath)
        if not p.is_dir():
            print(f"ERROR: --slugs-dir is not a directory: {p}")
            raise SystemExit(2)
        found = _slugs_from_dir(p)
        if not found:
            print(f"WARNING: --slugs-dir {p} contained no problem subdirs (meta.json).")
        extra += found
    if extra:
        # De-dupe while preserving order; keep any explicit --slug values too.
        seen = set(args.slug)
        for s in extra:
            if s not in seen:
                args.slug.append(s)
                seen.add(s)


# --------------------------------------------------------------------------- #
# audit
# --------------------------------------------------------------------------- #
def cmd_audit(args) -> int:
    col = _C(args.color)
    dirs = _select(list(_iter_problem_dirs(settings.content_dirs)),
                   args.slug, args.filter, args.limit)
    if not dirs:
        print("No problems selected.")
        return 0
    if not _preflight(args.base_url):
        print(f"ERROR: LLM server not reachable at {args.base_url} "
              f"(checked {args.base_url.rstrip('/')}/v1/models). Is it running?")
        return 1

    cp = _Checkpoint(_progress_path("audit"),
                     {"cmd": "audit", "model": args.model, "no_judge": args.no_judge}).load()
    if args.restart:
        cp.reset()
    elif (reason := cp.incompatible()):
        print(f"ERROR: progress log {cp.path} is from a different run ({reason} differ). "
              f"Pass --restart to start over, or delete it.")
        return 1

    total = len(dirs)
    remaining = [d for d in dirs if d.name not in cp.done]
    if cp.resuming:
        print(col.dim(f"Resuming: {len(cp.done)} done, {len(remaining)} left of {total}.\n"))
    print(f"Auditing {len(remaining)} problem(s) [{args.workers} workers, model={args.model}, "
          f"{'heuristic-only' if args.no_judge else 'judge'} mode]\n")

    def work(d):
        slug, statement, solution, hints = _load(d)
        if not hints:
            return {"slug": slug, "dir": str(d), "hints": [], "heuristic": {},
                    "verdicts": [], "flagged": [], "status": "no-hints", "judge_error": None}
        flags = leak_flags(hints)
        verdicts, jerr = [], None
        if not args.no_judge:
            try:
                verdicts = judge_hints(statement, solution, hints,
                                       base_url=args.base_url, model=args.model)["verdicts"]
            except Exception as e:  # noqa: BLE001
                jerr = f"{type(e).__name__}: {e}"
        flagged = sorted(set(flags) | {v["tier"] for v in verdicts if v["label"] != "ok"})
        return {"slug": slug, "dir": str(d), "hints": hints,
                "heuristic": {str(k): v for k, v in flags.items()},
                "verdicts": verdicts, "flagged": flagged,
                "status": _classify(flags, verdicts), "judge_error": jerr}

    tag = {"clean": col.green("clean"), "leak": col.red("LEAK "),
           "vague": col.yellow("vague"), "no-hints": col.dim("none "),
           "error": col.red("ERROR")}
    done_n, errors, interrupted = len(cp.done), 0, False
    cp.open()
    try:
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futs = {pool.submit(work, d): d for d in remaining}
            for fut in as_completed(futs):
                d = futs[fut]
                try:
                    r = fut.result()
                except Exception as e:  # noqa: BLE001
                    r = {"slug": d.name, "status": "error",
                         "judge_error": f"{type(e).__name__}: {e}"}
                # A judge/connection failure is transient — do NOT checkpoint it, so
                # the slug is retried on the next resume instead of marked done.
                if r["status"] == "error" or r.get("judge_error"):
                    errors += 1
                    print(f"     {col.red('ERROR')} {r['slug']}"
                          + col.dim(f"  ({r.get('judge_error')})"))
                    continue
                cp.record(r)
                done_n += 1
                extra = f" tiers={r['flagged']}" if r["flagged"] else ""
                print(f"[{done_n}/{total}] {tag.get(r['status'], r['status'])} {r['slug']}{extra}")
    except KeyboardInterrupt:
        interrupted = True
        print("\nInterrupted — progress saved; re-run `audit` to resume.")
    finally:
        cp.close()

    results = list(cp.done.values())
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps({
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "model": args.model, "base_url": args.base_url,
        "no_judge": args.no_judge, "count": len(results),
        "results": sorted(results, key=lambda r: r["slug"]),
    }, indent=2) + "\n", encoding="utf-8")

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"\n{col.bold('Summary')}  " + "  ".join(
        f"{k}={v}" for k, v in sorted(counts.items())))
    flagged = [r for r in results if r["status"] in ("leak", "vague")]
    if flagged:
        print(f"{col.bold('Worst offenders')} (leak first):")
        for r in sorted(flagged, key=lambda r: (r["status"] != "leak", r["slug"]))[:25]:
            print(f"  {tag.get(r['status'])} {r['slug']:40s} tiers={r['flagged']}")

    if not interrupted and errors == 0:
        cp.finalize()  # whole pass done — drop the resume log
    else:
        left = total - len([r for r in results if r["slug"] in {d.name for d in dirs}])
        print(col.yellow(f"\n{errors} error(s), {left} slug(s) not done — "
                         f"re-run `audit` to resume ({cp.path})."))
    print(f"\nReport: {REPORT_PATH}")
    print("Next:  python scripts/improve_hints.py fix --from-report --dry-run")
    return 1 if errors else 0


# --------------------------------------------------------------------------- #
# fix
# --------------------------------------------------------------------------- #
def cmd_fix(args) -> int:
    col = _C(args.color)
    baseline: dict[str, int] = {}
    slugs_from_report: set[str] | None = None
    if args.from_report:
        if not REPORT_PATH.exists():
            print(f"ERROR: no report at {REPORT_PATH}. Run `audit` first.")
            return 1
        report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
        slugs_from_report = set()
        for r in report["results"]:
            if r["flagged"]:
                slugs_from_report.add(r["slug"])
                baseline[r["slug"]] = len(r["flagged"])

    dirs = list(_iter_problem_dirs(settings.content_dirs))
    dirs = _select(dirs, args.slug, args.filter, 0)
    if slugs_from_report is not None:
        dirs = [d for d in dirs if _load(d)[0] in slugs_from_report]
    if args.limit and args.limit > 0:
        dirs = dirs[:args.limit]

    if not dirs:
        print("Nothing to fix (no flagged problems selected). "
              "Did you run `audit` and pass --from-report, or --slug/--filter?")
        return 0
    if not _preflight(args.base_url):
        print(f"ERROR: LLM server not reachable at {args.base_url}. Is it running?")
        return 1

    mode = col.yellow("DRY RUN") if not args.apply else col.green("APPLY")
    # Dry-run and apply keep separate logs so the normal dry-run -> apply flow never
    # collides on a leftover checkpoint.
    cp = _Checkpoint(_progress_path("fix-apply" if args.apply else "fix-dry"),
                     {"cmd": "fix", "model": args.model, "no_judge": args.no_judge,
                      "apply": bool(args.apply)}).load()
    if args.restart:
        cp.reset()
    elif (reason := cp.incompatible()):
        print(f"ERROR: progress log {cp.path} is from a different run ({reason} differ). "
              f"Pass --restart to start over, or delete it.")
        return 1

    total = len(dirs)
    remaining = [d for d in dirs if d.name not in cp.done]
    if cp.resuming:
        print(col.dim(f"Resuming: {len(cp.done)} done, {len(remaining)} left of {total}.\n"))
    print(f"Fixing {len(remaining)} problem(s) [{mode}, {args.workers} workers, "
          f"model={args.model}, tries={args.tries}]\n")

    def work(d):
        slug, statement, solution, old = _load(d)
        old_ct = baseline.get(slug)
        if old_ct is None and not args.no_baseline:
            try:
                ov = judge_hints(statement, solution, old, base_url=args.base_url,
                                 model=args.model)
                old_ct = len(set(leak_flags(old)) | set(ov["regenerate"]))
            except Exception:  # noqa: BLE001 - baseline is best-effort
                old_ct = None
        new, rec = generate_hints_verified(
            statement, solution, base_url=args.base_url, model=args.model,
            gen_thinking=getattr(args, "gen_thinking", False),
            use_judge=not args.no_judge, tries=args.tries)
        new_ct = len(rec["flagged"])
        # Overwrite only when we did not make it worse: accepted-clean, or fewer
        # flags than before, or no reliable baseline (trust the freshly-gated set).
        improved = rec["accepted"] or old_ct is None or new_ct < old_ct
        return d, slug, old, new, old_ct, new_ct, rec, improved

    # Seed running counts from any prior (resumed) records.
    wrote = sum(1 for r in cp.done.values() if r["outcome"] in ("wrote", "would"))
    skipped = sum(1 for r in cp.done.values() if r["outcome"] == "keep")
    empty = failed = 0
    done_n, interrupted = len(cp.done), False
    cp.open()
    try:
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futs = {pool.submit(work, d): d for d in remaining}
            for fut in as_completed(futs):
                d = futs[fut]
                try:
                    d, slug, old, new, old_ct, new_ct, rec, improved = fut.result()
                except Exception as e:  # noqa: BLE001 - transient: not checkpointed, retried on resume
                    failed += 1
                    print(f"     {col.red('FAIL')} {d.name}: {type(e).__name__}: {e}")
                    continue
                if not new:
                    empty += 1
                    print(f"     {col.dim('EMPTY')} {slug}: model returned nothing")
                    continue
                base = "?" if old_ct is None else str(old_ct)
                delta = f"flags {base}->{new_ct}" + ("" if rec["accepted"] else col.dim(" (residual)"))
                if improved and args.apply:
                    _write_hints(d, new)  # write FIRST, then checkpoint below
                    outcome, verb = "wrote", col.green("WROTE")
                    wrote += 1
                elif improved:
                    outcome, verb = "would", col.yellow("WOULD")
                    wrote += 1
                else:
                    outcome, verb = "keep", col.dim("KEEP ")
                    skipped += 1
                # The chosen set may be an earlier (least-flagged) round, not the
                # last one, so grab ITS judge verdicts for the compare report.
                chosen = next((a for a in rec["attempts"] if a["hints"] == new),
                              rec["attempts"][-1] if rec["attempts"] else {})
                # Checkpoint only after any meta.json write has landed, so a slug is
                # marked done exactly when its result is durable.
                cp.record({"slug": slug, "outcome": outcome, "old_ct": old_ct,
                           "new_ct": new_ct, "accepted": rec["accepted"],
                           "old": old, "new": new,
                           "new_verdicts": chosen.get("verdicts", []),
                           "new_heuristic": {str(k): v for k, v in chosen.get("heuristic", {}).items()},
                           "new_flagged": chosen.get("flagged", [])})
                done_n += 1
                print(f"[{done_n}/{total}] {verb} {slug:38s} {delta}")
                if args.verbose or not args.apply:
                    for j, (o, n) in enumerate(zip(old + [""] * 3, new + [""] * 3), 1):
                        if j > len(new):
                            break
                        print(col.dim(f"        old{j}: {o}"))
                        print(f"        new{j}: {n}")
    except KeyboardInterrupt:
        interrupted = True
        print("\nInterrupted — progress saved; re-run the same command to resume.")
    finally:
        cp.close()

    # Persist a durable old->new report (even on a partial/interrupted run) so the
    # proposed replacements can be reviewed in a browser via hint_compare_report.py,
    # mirroring how `audit` writes audit.json. Dry-run and apply keep separate files.
    fix_report = REPORT_PATH.parent / ("fix-apply.json" if args.apply else "fix-dry.json")
    if cp.done:
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        fix_report.write_text(json.dumps({
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "model": args.model, "base_url": args.base_url,
            "apply": bool(args.apply), "count": len(cp.done),
            "results": sorted(cp.done.values(), key=lambda r: r["slug"]),
        }, indent=2) + "\n", encoding="utf-8")

    if not interrupted and empty == 0 and failed == 0:
        cp.finalize()  # whole pass done — drop the resume log
    else:
        print(col.yellow(f"{empty} empty, {failed} failed, "
                         f"{'interrupted' if interrupted else 'incomplete'} — "
                         f"re-run to resume ({cp.path})."))

    verb = "wrote" if args.apply else "would-write"
    print(f"\nDone. {verb}={wrote} kept={skipped} empty={empty} failed={failed}"
          + ("" if args.apply else "  (dry run: nothing written)"))
    if cp.done:
        print(f"Compare report:  {fix_report}")
        print(f"Browse old->new: python scripts/hint_compare_report.py"
              + (" --apply" if args.apply else "") + " --open")
    if wrote and args.apply:
        print("Reseed to load into the DB:  python scripts/seed.py")
        print("Re-audit to confirm:         python scripts/improve_hints.py audit")
    return 1 if failed else 0


# --------------------------------------------------------------------------- #
# calibrate
# --------------------------------------------------------------------------- #
def cmd_calibrate(args) -> int:
    col = _C(args.color)
    if not _preflight(args.base_url):
        print(f"ERROR: LLM server not reachable at {args.base_url}. Is it running?")
        return 1
    data = json.loads(EXEMPLARS_PATH.read_text(encoding="utf-8"))
    exemplars = data["exemplars"]
    if args.slug:
        exemplars = [e for e in exemplars if e["slug"] in set(args.slug)]

    def load(slug):
        d = ROOT / "content" / "problems" / slug
        st = (d / "problem.md").read_text(encoding="utf-8") if (d / "problem.md").exists() else slug
        so = (d / "solution" / "solution.py").read_text(encoding="utf-8") if (d / "solution" / "solution.py").exists() else ""
        return st, so

    gold_pass = gold_total = leak_caught = leak_total = 0
    for e in exemplars:
        slug = e["slug"]
        st, so = load(slug)
        # 1) gold set must grade all ok
        gv = judge_hints(st, so, e["gold"], base_url=args.base_url, model=args.model)
        gflag = gv["regenerate"]
        gold_total += 1
        gold_ok = not gflag
        gold_pass += 1 if gold_ok else 0
        line = f"{slug:44s} gold->{'OK' if gold_ok else 'FLAGGED ' + str(gflag)}"
        # 2) if a known leak exists, dropping it into the last tier must be caught
        if e.get("leak"):
            leak_total += 1
            probe = e["gold"][:-1] + [e["leak"]]
            lv = judge_hints(st, so, probe, base_url=args.base_url, model=args.model)
            caught = len(probe) in set(lv["regenerate"]) or bool(leak_flags(probe))
            leak_caught += 1 if caught else 0
            line += f"   leak->{'CAUGHT' if caught else col.red('MISSED')}"
        print((col.green(line) if gold_ok else col.yellow(line)))

    print(f"\n{col.bold('Calibration')}  gold ok: {gold_pass}/{gold_total}"
          f"   leaks caught: {leak_caught}/{leak_total}")
    ok = gold_pass == gold_total and leak_caught == leak_total
    print(col.green("Judge is well-calibrated.") if ok
          else col.yellow("Judge disagrees on some exemplars — consider tuning the rubric."))
    return 0 if ok else 2


# --------------------------------------------------------------------------- #
# apply-report — write the already-reviewed hints from a fix dry-run report
# --------------------------------------------------------------------------- #
def cmd_apply_report(args) -> int:
    """Write the `new` hints stored in a fix report verbatim — no regeneration.

    `fix --apply` re-generates from scratch (temperature > 0), so the text it writes
    differs from the dry-run you reviewed. This subcommand instead writes exactly the
    sets recorded in .hints/fix-dry.json for the strictly-better problems, so the
    on-disk result matches the before->after page. Deterministic and offline (no LLM).
    """
    col = _C(args.color)
    report_path = (args.report if args.report else
                   REPORT_PATH.parent / ("fix-apply.json" if args.from_apply else "fix-dry.json"))
    if not report_path.exists():
        print(f"ERROR: no report at {report_path}. "
              f"Run `improve_hints.py fix --from-report --dry-run` first.")
        return 1
    report = json.loads(report_path.read_text(encoding="utf-8"))

    # slug -> dir and slug -> current on-disk hints (read cheaply from meta.json only)
    dir_by_slug: dict[str, pathlib.Path] = {}
    cur_by_slug: dict[str, list] = {}
    for d in _iter_problem_dirs(settings.content_dirs):
        meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
        s = meta.get("slug", d.name)
        dir_by_slug[s] = d
        cur_by_slug[s] = normalize_hints(meta.get("hints"))

    wanted = set(args.slug)
    selected = []
    for r in report["results"]:
        if r.get("outcome") not in ("would", "wrote"):   # strictly-better only
            continue
        if args.clean_only and not r.get("accepted"):
            continue
        if wanted and r["slug"] not in wanted:
            continue
        if args.filter and args.filter not in r["slug"]:
            continue
        selected.append(r)
    if args.limit and args.limit > 0:
        selected = selected[:args.limit]

    if not selected:
        print("Nothing to write (no strictly-better results matched the selection).")
        return 0

    mode = col.green("APPLY") if args.apply else col.yellow("DRY RUN")
    clean_n = sum(1 for r in selected if r.get("accepted"))
    print(f"Applying {len(selected)} reviewed hint set(s) from {report_path.name} "
          f"[{mode}]  (clean {clean_n} / residual {len(selected) - clean_n})\n")

    wrote = noop = missing = empty = 0
    for r in sorted(selected, key=lambda r: r["slug"]):
        slug = r["slug"]
        d = dir_by_slug.get(slug)
        if d is None:
            missing += 1
            print(f"  {col.red('MISSING')} {slug}: no matching problem dir")
            continue
        new = normalize_hints(r.get("new"))
        if not new:
            empty += 1
            print(f"  {col.dim('EMPTY')}   {slug}: report has no new hints")
            continue
        if cur_by_slug.get(slug) == new:   # already on disk (idempotent re-run)
            noop += 1
            continue
        tag = (f"{r.get('old_ct','?')}->{r.get('new_ct','?')} flags"
               + ("" if r.get("accepted") else col.dim(" (residual)")))
        if args.apply:
            _write_hints(d, new)
            print(f"  {col.green('WROTE')} {slug:44s} {tag}")
        else:
            print(f"  {col.yellow('WOULD')} {slug:44s} {tag}")
        wrote += 1

    verb = "wrote" if args.apply else "would-write"
    print(f"\nDone. {verb}={wrote} unchanged={noop} empty={empty} missing={missing}"
          + ("" if args.apply else "  (dry run: nothing written)"))
    if wrote and args.apply:
        print("Reseed to load into the DB:  python scripts/seed.py")
        print("Re-audit to confirm:         python scripts/improve_hints.py audit")
    return 1 if missing else 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main() -> int:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--base-url", default=LLM_SERVER_URL,
                        help=f"LLM server base URL (default {LLM_SERVER_URL})")
    parent.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"model name to request (default {DEFAULT_MODEL})")
    parent.add_argument("--workers", type=int, default=4,
                        help="parallel requests (match the server's slot count; default 4)")
    parent.add_argument("--slug", action="append", default=[],
                        help="only this slug (repeatable)")
    parent.add_argument("--slugs", action="append", default=[], metavar="A,B,C",
                        help="comma-separated list of slugs (repeatable; combines with --slug)")
    parent.add_argument("--slugs-file", action="append", default=[], metavar="PATH",
                        help="file with one slug per line (# comments/blank lines ignored; repeatable)")
    parent.add_argument("--slugs-dir", action="append", default=[], metavar="DIR",
                        help="select every problem subdir (with a meta.json) under DIR (repeatable)")
    parent.add_argument("--filter", default="",
                        help="only slugs containing this substring")
    parent.add_argument("--limit", type=int, default=0, help="cap problems processed (0=all)")
    parent.add_argument("--no-judge", action="store_true",
                        help="heuristic pre-filter only; skip the (slow) LLM judge")
    parent.add_argument("--restart", action="store_true",
                        help="ignore any saved progress log and start the run from scratch")
    parent.add_argument("--no-color", dest="color", action="store_false",
                        help="disable ANSI colors")
    parent.set_defaults(color=sys.stdout.isatty())

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    pa = sub.add_parser("audit", parents=[parent], help="grade existing hints; write a report")
    pa.set_defaults(func=cmd_audit)

    pf = sub.add_parser("fix", parents=[parent], help="regenerate flagged hint sets")
    pf.add_argument("--from-report", action="store_true",
                    help=f"take the flagged problems from {REPORT_PATH}")
    pf.add_argument("--apply", action="store_true",
                    help="write meta.json (default is a dry run)")
    pf.add_argument("--dry-run", action="store_true",
                    help="preview only; the default (explicit opposite of --apply). --apply wins if both given.")
    pf.add_argument("--tries", type=int, default=3,
                    help="max generate/regenerate rounds per problem (default 3)")
    pf.add_argument("--gen-thinking", action="store_true",
                    help="let the generator reason before drafting (slower; off by "
                         "default so it stays conceptual and doesn't re-derive/leak "
                         "the recurrence). The judge always thinks.")
    pf.add_argument("--no-baseline", action="store_true",
                    help="don't judge the old hints first; always write the new gated set")
    pf.add_argument("-v", "--verbose", action="store_true",
                    help="print old->new hints even in --apply mode")
    pf.set_defaults(func=cmd_fix)

    pc = sub.add_parser("calibrate", parents=[parent],
                        help="check the judge against app/llm/hint_exemplars.json")
    pc.set_defaults(func=cmd_calibrate)

    pw = sub.add_parser("apply-report", parents=[parent],
                        help="write reviewed hints from a fix dry-run report (no regeneration)")
    pw.add_argument("--report", type=pathlib.Path, default=None,
                    help=f"report to apply (default {REPORT_PATH.parent / 'fix-dry.json'})")
    pw.add_argument("--from-apply", action="store_true",
                    help="default to fix-apply.json instead of fix-dry.json")
    pw.add_argument("--apply", action="store_true", help="write meta.json (default is a dry run)")
    pw.add_argument("--dry-run", action="store_true", help="preview only (the default)")
    pw.add_argument("--clean-only", action="store_true",
                    help="write only fully-clean sets; skip residual (still-flagged) ones")
    pw.set_defaults(func=cmd_apply_report)

    args = ap.parse_args()
    _resolve_slugs(args)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
