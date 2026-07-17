#!/usr/bin/env python3
"""Validate and bulk-import a staging folder of fully-generated problems.

Input layout (what the Mode-A generator + statement staging produce) is one
colocated directory per slug:

    <src>/<slug>/meta.json                   # title + body (statement prose)
    <src>/<slug>/generated_full_problem.json # the runnable "core": kind, contract
                                             #   (function OR class), compare,
                                             #   starter, canonical, tests, hints, tags
    <src>/<slug>/assets/                      # optional statement figures (png/jpg/gif/svg)

Title and body come from ``meta.json``; everything the judge needs comes from
``generated_full_problem.json`` (where the two disagree on tags/difficulty by
design, the generated core wins — it is what was verified). Both problem kinds
are supported: ``kind="function"`` (one top-level function) and ``kind="class"``
(a stateful "design" problem whose tests replay ``{operations, args}``).

This is the **gate** between such a folder and the live app. It reuses — never
re-implements — every guardrail the project already has, cheapest → most
expensive, short-circuiting so untrusted code never runs for a structurally
broken slug:

  1. **Presence / slug** — each dir needs both JSON files, valid JSON, a non-empty
     ``title``, and a kebab-case slug.
  2. **Structural** — ``scripts/test_llm_output.py`` (strict pydantic + AST):
     kind-aware required fields, valid signatures, per-test ``input`` keys ==
     params / ``{operations, args}``, compare-mode shape, hints cap,
     JSON-serializable values. ``--strict`` promotes its warnings to failures.
  3. **Slug collision** — a slug already in **another** content root or the DB is a
     genuine bank-wide duplicate (slugs are unique across roots), so it is skipped.
     A slug already in the **target** root is skipped too unless ``--overwrite``
     replaces it deliberately.
  4. **Behavioral** — the canonical solution must pass **all** its own tests in the
     real sandbox (``app.executor.run_submission``, via ``audit.audit_problem``).
  5. **Statement ↔ judge consistency** — ``scripts/audit.py``'s per-problem audit:
     a statement promising "any order" must not use ``compare=exact``; for relaxed
     modes a re-ordered valid answer must still be accepted (skipped for class
     problems, which are always ``compare=exact``).

Only slugs that clear **all** of these qualify. The script prints a full report,
asks for confirmation (``--yes`` to skip), then imports the qualifying ones the
durable way: writes each to the target content root (default
``content/problems-extended/`` — the gitignored extended set; ``--out`` to choose,
e.g. ``content/problems`` for the committed default set), copies its figures,
reloads it from disk, upserts it into the DB, and re-verifies it once more from
the DB — the same round-trip ``scripts/seed.py`` uses.

``STAGING`` below is any staging dir of ``<slug>/`` subdirs (the folder name is
arbitrary — whatever your batch was generated into).

Usage:
    python scripts/import_generated_problems.py STAGING
    python scripts/import_generated_problems.py STAGING --dry-run    # check only
    python scripts/import_generated_problems.py STAGING -y           # no prompt
    python scripts/import_generated_problems.py STAGING --overwrite  # replace on slug hit
    python scripts/import_generated_problems.py STAGING --slug min-stack -v
    python scripts/import_generated_problems.py STAGING --out content/problems

Exit status: 0 when the run is clean (everything qualified and — unless
--dry-run — imported); 1 when some slug failed a check or the user declined; 2 on
a usage / layout error.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))  # scripts/ is not a package

# Reuse the project's existing, tested machinery — this script only orchestrates.
import audit  # noqa: E402  - scripts/audit.py: behavioral + statement<->judge consistency
import test_llm_output as tlo  # noqa: E402  - strict structural (pydantic + AST) validator
import verify_json as vj  # noqa: E402  - run_submission wrapper w/ per-test failure detail
from app import content, store  # noqa: E402
from app.config import settings  # noqa: E402
from app.db import SessionLocal, init_db  # noqa: E402
from app.models import Problem  # noqa: E402
from app.executor import run_submission  # noqa: E402
from app.tags import unknown_tags  # noqa: E402

DEFAULT_OUT = ROOT / "content" / "problems-extended"
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Rewrite a relative figure ref in the staged body onto the served path. Staged
# bodies write `![](assets/foo.png)`; the app serves figures at
# `/problems/<slug>/assets/<file>` (see docs/problem-images.md).
_ASSET_REF = re.compile(r"\]\(\s*(?:\./)?assets/")


@dataclass
class Candidate:
    """One slug's verdict after all checks. ``data`` is the assembled problem dict
    ready for ``content.write_problem_files`` — populated only when it qualifies."""
    slug: str
    ok: bool = False
    reason: str = ""                       # why it was disqualified (empty when ok)
    warnings: list[str] = field(default_factory=list)
    detail: list[str] = field(default_factory=list)  # extra lines under the row (-v)
    kind: str = "?"
    difficulty: str = "?"
    compare: str = "?"
    n_tests: int = 0
    n_hints: int = 0
    overwrites: bool = False               # will replace an existing target-root dir
    data: dict | None = None               # the problem dict to import
    asset_src: Path | None = None          # <slug>/assets to copy on import


def _rewrite_asset_paths(body: str, slug: str) -> str:
    return _ASSET_REF.sub(f"](/problems/{slug}/assets/", body)


def _problem_ns(gen: dict, statement: str) -> SimpleNamespace:
    """A Problem-like stand-in with exactly the attributes ``run_submission`` and
    ``audit.audit_problem`` read — kind-aware, mirroring ``verify_json.grade``.

    For a class problem ``function_name`` falls back to the class name (the
    executor reads it unconditionally; the harness ignores it)."""
    tests = [
        SimpleNamespace(
            name=t.get("name", f"test-{i + 1}"), input=t.get("input", {}),
            expected=t.get("expected"), weight=t.get("weight", 1),
            hidden=t.get("hidden", False),
        )
        for i, t in enumerate(gen.get("tests", []))
    ]
    return SimpleNamespace(
        kind=gen.get("kind", "function"),
        function_name=(gen.get("function_name") or gen.get("class_name") or "").strip(),
        params=gen.get("params", []),
        return_type=(gen.get("return_type") or "").strip(),
        class_name=((gen.get("class_name") or "").strip() or None),
        class_methods=(gen.get("class_methods") or None),
        compare=gen.get("compare", "exact"),
        canonical_solution=gen.get("canonical_solution", ""),
        statement_md=statement,
        time_limit_ms=settings.EXEC_TIME_LIMIT_MS,
        memory_limit_mb=settings.EXEC_MEMORY_LIMIT_MB,
        points=100,
        tests=tests,
    )


def _behavioral_detail(gen: dict) -> list[str]:
    """Per-failing-test lines (status / expected / actual) for the report, reusing
    the same grade path as scripts/verify_json.py."""
    lines: list[str] = []
    try:
        g = vj.grade(gen)
    except Exception as exc:  # noqa: BLE001 - report any judge/runtime failure
        return [f"could not run canonical: {exc}"]
    lines.append(f"{g.passed_count}/{g.total_count} tests passed")
    for i, r in enumerate(g.results):
        if r.passed:
            continue
        line = f"- {r.name} [{r.status}]"
        if r.error:
            line += f": {r.error}"
        lines.append(line)
        if r.status == "wrong":
            exp = gen["tests"][i].get("expected")
            lines.append(f"    expected={json.dumps(exp)}")
            lines.append(f"    actual  ={json.dumps(r.returned)}")
    return lines


def _problem_dict(slug: str, title: str, body: str, gen: dict,
                  hints: list[str]) -> dict:
    """Combine the two sources into the dict ``content.write_problem_files`` wants.
    Title/body from ``meta.json``; everything load-bearing from
    ``generated_full_problem.json``. Limits/scoring fall to write_problem_files'
    defaults; relative image refs are rewritten to the served URL so they resolve
    once ``assets/`` is copied alongside.

    The body is stored as-is (asset refs rewritten); it must NOT be prefixed with
    an ``# {title}`` heading — the problem page renders ``prob.title`` on its own,
    so a leading H1 in the statement would show the title twice."""
    statement = _rewrite_asset_paths(body, slug).rstrip() + "\n"
    return {
        "slug": slug,
        "title": title,
        "difficulty": gen.get("difficulty", "medium"),
        "topics": gen.get("tags", []),          # write_problem_files normalizes
        "hints": hints,                          # already normalized (≤ MAX_HINTS)
        "statement_md": statement,
        "kind": gen.get("kind", "function"),
        "function_name": gen.get("function_name", ""),
        "return_type": gen.get("return_type", ""),
        "params": gen.get("params", []),
        "class_name": gen.get("class_name"),
        "class_methods": gen.get("class_methods"),
        "compare": gen.get("compare", "exact"),
        "starter_code": gen.get("starter_code", ""),
        "canonical_solution": gen.get("canonical_solution", ""),
        "tests": gen.get("tests", []),
    }


# ---------------------------------------------------------------------------
# Per-slug validation. Ordered cheapest → most expensive; the first failure
# short-circuits so we never run untrusted code in the sandbox for a slug that
# is already structurally broken.
# ---------------------------------------------------------------------------
def check_slug(src_dir: Path, out_slugs: set[str], foreign: dict[str, str],
               *, strict: bool, allow_overwrite: bool) -> Candidate:
    slug = src_dir.name
    c = Candidate(slug=slug)
    meta_path = src_dir / "meta.json"
    gen_path = src_dir / "generated_full_problem.json"

    # 1) presence + valid slug ------------------------------------------------
    if not SLUG_RE.match(slug):
        c.reason = "slug is not lowercase kebab-case"
        return c
    if not meta_path.is_file():
        c.reason = "missing meta.json"
        return c
    if not gen_path.is_file():
        c.reason = "missing generated_full_problem.json"
        return c

    # 2) meta.json valid + title + body --------------------------------------
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        c.reason = f"meta.json is not valid JSON ({exc})"
        return c
    title = (meta.get("title") if isinstance(meta, dict) else None) or ""
    if not str(title).strip():
        c.reason = "meta.json has no non-empty 'title'"
        return c
    title = str(title).strip()
    body = str(meta.get("body", "") or "")
    if not body.strip():
        c.reason = "meta.json has no non-empty 'body'"
        return c

    # 3) generated_full_problem.json valid JSON ------------------------------
    try:
        gen = json.loads(gen_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        c.reason = f"generated_full_problem.json is not valid JSON ({exc})"
        return c
    if not isinstance(gen, dict):
        c.reason = "generated_full_problem.json is not a JSON object"
        return c

    # 4) STRUCTURAL — strict core-contract validation (test_llm_output.py) ----
    #    Kind-aware and hints-aware (hints are a first-class field there).
    rep = tlo.validate(gen, strict=strict)
    if rep.errors:
        c.reason = "structural: " + rep.errors[0]
        c.detail = [f"ERROR: {e}" for e in rep.errors[1:]]
        return c
    if strict and rep.warnings:
        c.reason = "structural (strict): " + rep.warnings[0]
        c.detail = [f"WARN: {w}" for w in rep.warnings[1:]]
        return c
    # Keep test_llm_output's warnings except its blanket "not canonical" tag note:
    # it fires even for aliases that fold cleanly. We replace it below with the
    # precise "won't fold" signal from unknown_tags.
    c.warnings.extend(w for w in rep.warnings if not w.lstrip().lower().startswith("tags:"))
    c.kind = gen.get("kind", "function")
    c.difficulty = gen.get("difficulty", "?")
    c.compare = gen.get("compare", "?")
    c.n_tests = len(gen.get("tests", []))
    hints = content.normalize_hints(gen.get("hints"))
    c.n_hints = len(hints)

    # Surface (but don't block on) tags that are neither canonical nor a known
    # alias — normalize_tags passes these through unchanged (persist as-is).
    unk = unknown_tags(gen.get("tags"))
    if unk:
        c.warnings.append(f"non-canonical tag(s) {unk} not in vocabulary — "
                          "will persist as-is (see specs/tags.md)")

    # 5) SLUG COLLISION -------------------------------------------------------
    #    A slug in ANOTHER content root or the DB (but not the target root) is a
    #    bank-wide duplicate --overwrite can't fix (it wouldn't remove the other
    #    copy) — hard skip. A slug in the TARGET root is a deliberate replace.
    if slug in foreign:
        c.reason = (f"slug already exists in {foreign[slug]} (unique bank-wide) — "
                    "reconcile manually; --overwrite cannot resolve a cross-root hit")
        return c
    if slug in out_slugs:
        if not allow_overwrite:
            c.reason = ("slug already exists in the target root — possible duplicate; "
                        "skipped (use --overwrite to replace deliberately)")
            return c
        c.overwrites = True

    # 6) BEHAVIORAL + 7) CONSISTENCY — one sandbox run via audit.audit_problem.
    #    Its step 1 IS the authoritative behavioral check (canonical passes all
    #    tests in the real sandbox); steps 2-3 are the statement<->judge audit.
    statement = body   # audit reads statement_md for "any order" language; no title heading (see _problem_dict)

    refs = re.findall(r"\]\(\s*(?:\./)?assets/([^)]+)\)", body)
    assets_dir = src_dir / "assets"
    if refs:
        gone = [r for r in refs if not (assets_dir / r).is_file()]
        if gone:
            c.warnings.append(f"statement references missing asset(s): {sorted(set(gone))}")
    if assets_dir.is_dir() and any(assets_dir.iterdir()):
        c.asset_src = assets_dir

    ns = _problem_ns(gen, statement)
    issues = audit.audit_problem(ns)
    if not ns._canon:  # canonical did NOT pass all its tests
        c.reason = "behavioral: canonical solution fails its own tests"
        c.detail = _behavioral_detail(gen)
        return c
    consistency = [i for i in issues if "pass all its tests" not in i
                   and "no canonical" not in i]
    if consistency:
        c.reason = "consistency: " + consistency[0]
        c.detail = [f"- {i}" for i in consistency[1:]]
        return c

    # Qualified — assemble the durable problem dict for import.
    c.ok = True
    c.data = _problem_dict(slug, title, body, gen, hints)
    return c


# ---------------------------------------------------------------------------
# Import: write the durable mirror, copy figures, reload, upsert, re-verify.
# ---------------------------------------------------------------------------
def _copy_assets(c: Candidate, out_dir: Path) -> None:
    """Copy the statement's figures into <out>/<slug>/assets/ (binary-safe).
    write_problem_files' own `assets` map is text-only (SVG); these may be
    jpg/png/gif, so copy the files as bytes."""
    if c.asset_src is None:
        return
    dst = out_dir / c.slug / "assets"
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(c.asset_src.iterdir()):
        if f.is_file():
            shutil.copy2(f, dst / f.name)


def import_candidates(cands: list[Candidate], out_dir: Path) -> int:
    """Write + seed + re-verify each qualifying candidate. Returns the number that
    round-tripped cleanly (written to disk AND passing all tests from the DB)."""
    init_db()
    imported = 0
    with SessionLocal() as db:
        for c in cands:
            assert c.data is not None
            if c.overwrites:
                shutil.rmtree(out_dir / c.slug, ignore_errors=True)
            content.write_problem_files(c.data, content_dir=out_dir)  # durable mirror
            _copy_assets(c, out_dir)                                  # binary figures, if any
            # Reload from disk so the DB matches exactly what was written (the same
            # path scripts/seed.py uses), then upsert that.
            reloaded = content.load_problem_dir(out_dir / c.slug)
            prob = store.upsert_problem(db, reloaded)
            g = run_submission(prob.canonical_solution, prob, prob.tests)
            tag = "overwrote" if c.overwrites else "imported"
            if g.solved:
                imported += 1
                print(f"  [OK]   {c.slug}: {tag} + verified "
                      f"({g.passed_count}/{g.total_count})")
            else:
                # Should be unreachable (it passed pre-import); surface loudly.
                print(f"  [WARN] {c.slug}: {tag} but DB re-verify FAILED "
                      f"({g.passed_count}/{g.total_count}) — investigate")
    return imported


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def print_report(cands: list[Candidate], verbose: bool) -> None:
    print(f"\n{'slug':40} {'status':9} {'kind':8} {'diff':7} {'compare':11} {'tests':5} {'hints':5}")
    print("-" * 96)
    for c in sorted(cands, key=lambda x: (not x.ok, x.slug)):
        status = "QUALIFY" if c.ok else "SKIP"
        row = (f"{c.slug:40} {status:9} {c.kind:8} {c.difficulty:7} {c.compare:11} "
               f"{c.n_tests or '':<5} {c.n_hints or '':<5}")
        if c.overwrites:
            row += "  (overwrites existing)"
        print(row)
        if not c.ok:
            print(f"    -> {c.reason}")
        for w in c.warnings:
            print(f"    . warn: {w}")
        if verbose:
            for d in c.detail:
                print(f"      {d}")


def confirm(n: int, out_dir: Path) -> bool:
    try:
        ans = input(f"\nImport {n} qualifying problem(s) into {out_dir} and the DB? [y/N] ")
    except EOFError:
        print("no TTY for confirmation; re-run with --yes to import non-interactively.")
        return False
    return ans.strip().lower() in ("y", "yes")


def _partition_existing(out_dir: Path) -> tuple[set[str], dict[str, str]]:
    """Return (out_slugs, foreign) where ``out_slugs`` are slugs already in the
    target root and ``foreign`` maps every slug present in ANOTHER content root or
    the DB (but not the target root) to a human label of where it lives. Slugs are
    unique bank-wide, so a foreign hit is a hard collision."""
    out_dir = out_dir.resolve()

    def _root_slugs(root: Path) -> set[str]:
        if not root.exists():
            return set()
        return {p.name for p in root.iterdir()
                if p.is_dir() and (p / "meta.json").exists()}

    out_slugs = _root_slugs(out_dir)
    foreign: dict[str, str] = {}
    for root in settings.content_dirs:
        if root.resolve() == out_dir:
            continue
        for s in _root_slugs(root):
            foreign.setdefault(s, root.name)
    # The DB is seeded from all roots; a DB slug not in the target root is foreign.
    try:
        init_db()
        with SessionLocal() as db:
            for (s,) in db.query(Problem.slug).all():
                if s not in out_slugs:
                    foreign.setdefault(s, "the DB")
    except Exception as exc:  # noqa: BLE001 - a missing/locked DB shouldn't hide disk hits
        print(f"note: could not read the DB for collision check ({exc}); "
              "using content roots only.")
    return out_slugs, foreign


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path,
                    help="staging dir of <slug>/{meta.json, generated_full_problem.json}")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help=f"content root to write into (default: {DEFAULT_OUT})")
    ap.add_argument("--slug", default=None, help="validate/import only this one slug")
    ap.add_argument("-y", "--yes", action="store_true",
                    help="skip the confirmation prompt (import all that qualify)")
    ap.add_argument("--dry-run", action="store_true",
                    help="run every check and report, but never write/import")
    ap.add_argument("--overwrite", action="store_true",
                    help="deliberately replace a problem whose slug already exists in "
                         "the target root (default: skip it as a possible duplicate)")
    ap.add_argument("--strict", action="store_true",
                    help="treat structural warnings as disqualifying too")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print per-test / per-error detail under each row")
    args = ap.parse_args(argv)

    if not args.src.is_dir():
        print(f"error: {args.src} is not a directory", file=sys.stderr)
        return 2
    src_dirs = sorted(p for p in args.src.iterdir()
                      if p.is_dir() and (args.slug is None or p.name == args.slug))
    if not src_dirs:
        where = f" matching --slug {args.slug}" if args.slug else ""
        print(f"No <slug>/ dirs found under {args.src}{where}.")
        return 0 if not args.slug else 2

    args.out.mkdir(parents=True, exist_ok=True)
    out_slugs, foreign = _partition_existing(args.out)

    print(f"Validating {len(src_dirs)} slug(s) from {args.src} -> {args.out} ...")
    cands = [check_slug(d, out_slugs, foreign, strict=args.strict,
                        allow_overwrite=args.overwrite) for d in src_dirs]

    print_report(cands, args.verbose)

    qualifying = [c for c in cands if c.ok]
    n_ok, n_skip = len(qualifying), len(cands) - len(qualifying)
    print("\n" + "-" * 90)
    print(f"{len(cands)} slug(s): {n_ok} qualify, {n_skip} skipped.")

    if args.dry_run:
        print("--dry-run: nothing written.")
        return 0 if n_skip == 0 else 1
    if not qualifying:
        print("Nothing to import.")
        return 1 if n_skip else 0
    if not (args.yes or confirm(n_ok, args.out)):
        print("Aborted — nothing imported.")
        return 1

    print(f"\nImporting {n_ok} problem(s) ...")
    imported = import_candidates(qualifying, args.out)
    print(f"\nDone: {imported}/{n_ok} imported and verified into {args.out} and the DB.")
    if n_skip:
        print(f"({n_skip} slug(s) were skipped — see the report above.)")
    # Non-zero if anything was skipped or an import failed to re-verify, so a CI
    # or scripted caller notices an imperfect run.
    return 0 if (imported == n_ok and n_skip == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
