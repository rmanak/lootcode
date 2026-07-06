#!/usr/bin/env python3
"""Validate and bulk-import a *collection* of ready-made problems into the bank.

A collection directory has this shape (see the two-part split below):

    <dir>/
    ├── statements/<slug>/problem.md   # the statement (Markdown) — imported verbatim
    ├── statements/<slug>/meta.json    # only its "title" is used; everything else ignored
    └── rest/<slug>.json               # the runnable "core": function contract,
                                        # compare mode, starter, canonical, tests, etc.

The ``rest/<slug>.json`` file is exactly the LLM "core contract"
(``specs/problem-schema.md`` / ``docs/problem-generation.md``) that
``scripts/test_llm_output.py`` validates and ``app/llm/generator.py`` emits:
``{difficulty, tags, function_name, params, return_type, compare, starter_code,
canonical_solution, tests}``. The statement + title live separately so the model
that produced the core never had to re-emit (and risk drifting from) the
statement.

Two optional extras are honored when present:
  * **``hints``** (a list of up to 3 short strings) — lifted out before the strict
    core validation (which forbids unknown keys), normalized (``normalize_hints``),
    and written to ``meta.json``. Absent ⇒ the problem simply has no hints.
  * **``statements/<slug>/assets/``** — binary figures (jpg/png) are copied into
    ``content/problems/<slug>/assets/`` and the statement's ``](assets/…)`` refs
    are rewritten to the served ``/problems/<slug>/assets/…`` URL.

**Tags** are advisory: non-canonical tags never block an import. Known aliases
fold on write (``normalize_tags``, e.g. ``bfs`` → ``breadth-first-search``); a tag
that is neither canonical nor a known alias persists **as-is** and is reported as
a warning so the owner can fold it into ``specs/tags.md`` later.

**Duplicate detection** here is *only* the exact slug collision below — the
broader near-duplicate detector (rephrasings / reduction-equivalent problems) in
``docs/duplicate-detection-plan.md`` is proposed but not built, so there is
nothing more to call. If/when ``app/dedup.py`` lands, add it as a gate here.

This script is the **gate** between such a folder and the live app. It reuses —
never re-implements — every guardrail the project already has:

  1. **Pairing / presence** — each slug must have all three files, valid JSON,
     and a non-empty ``title``; matching kebab-case slugs on both sides.
  2. **Structural** — ``scripts/test_llm_output.py`` (strict pydantic + AST):
     required fields, valid signatures, ``input`` keys == params, compare-mode
     shape, at least one visible + one hidden test, JSON-serializable values.
  3. **Slug collision** — a slug already in ``content/problems/`` or the DB is
     the cheapest signal of a genuine duplicate, so by policy it is **skipped,
     not silently overwritten** (docs/problem-generation.md). ``--overwrite``
     turns that into a deliberate, chosen replacement.
  4. **Behavioral** — the canonical solution must pass **all** its own tests in
     the real sandbox (``app.executor.run_submission``, via ``audit`` below).
  5. **Statement ↔ judge consistency** — ``scripts/audit.py``'s per-problem audit:
     a statement promising "any order" must not use ``compare=exact``, and for
     relaxed modes a deliberately re-ordered valid answer must still be accepted.

Only slugs that clear **all** of these qualify. The script prints a full report,
asks for confirmation, then imports the qualifying problems the durable way:
writes each to ``content/problems/<slug>/`` (the human-editable mirror), reloads
it from disk, upserts it into the DB, and re-verifies it once more from the DB.

Usage:
    python scripts/import_collection.py user_collection
    python scripts/import_collection.py user_collection --dry-run    # check only
    python scripts/import_collection.py user_collection -y           # no prompt
    python scripts/import_collection.py user_collection --overwrite   # replace on slug hit
    python scripts/import_collection.py user_collection -v --strict   # detail + warnings fatal

Exit status: 0 when the run is clean (everything qualified and — unless
--dry-run — was imported, or nothing needed doing); 1 when some slug failed a
check or the user declined; 2 on a usage / layout error.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys
from dataclasses import dataclass, field
from types import SimpleNamespace

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

# Reuse the project's existing, tested machinery — this script only orchestrates.
import audit  # noqa: E402  - scripts/audit.py: statement<->judge consistency + fairness
import test_llm_output as tlo  # noqa: E402  - strict structural (pydantic + AST) core validator
import verify_json as vj  # noqa: E402  - run_submission wrapper w/ per-test failure detail
from app import content, store  # noqa: E402
from app.config import settings  # noqa: E402
from app.db import SessionLocal, init_db  # noqa: E402
from app.executor import run_submission  # noqa: E402
from app.models import Problem  # noqa: E402
from app.tags import unknown_tags  # noqa: E402

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


@dataclass
class Candidate:
    """One slug's verdict after all checks. ``data`` is the assembled problem dict
    ready for ``content.write_problem_files`` — populated only when it qualifies."""
    slug: str
    ok: bool = False
    reason: str = ""                       # why it was disqualified (empty when ok)
    warnings: list[str] = field(default_factory=list)
    detail: list[str] = field(default_factory=list)  # extra lines under the row (-v)
    difficulty: str = "?"
    compare: str = "?"
    n_tests: int = 0
    n_hints: int = 0
    overwrites: bool = False               # will replace an existing problem
    data: dict | None = None               # the problem dict to import
    asset_src: pathlib.Path | None = None  # statements/<slug>/assets to copy on import


# ---------------------------------------------------------------------------
# Per-slug validation. Ordered cheapest → most expensive; the first failure
# short-circuits so we never run untrusted code in the sandbox for a slug that
# is already structurally broken.
# ---------------------------------------------------------------------------
def check_slug(slug: str, coll: pathlib.Path, existing: set[str],
               *, strict: bool, allow_overwrite: bool) -> Candidate:
    c = Candidate(slug=slug)
    stmt_dir = coll / "statements" / slug
    rest_path = coll / "rest" / f"{slug}.json"
    md_path = stmt_dir / "problem.md"
    meta_path = stmt_dir / "meta.json"

    # 1) presence + valid slug ------------------------------------------------
    if not SLUG_RE.match(slug):
        c.reason = "slug is not lowercase kebab-case"
        return c
    if not stmt_dir.is_dir():
        c.reason = f"missing statements/{slug}/ (no problem.md + meta.json)"
        return c
    if not rest_path.is_file():
        c.reason = f"missing rest/{slug}.json"
        return c
    if not md_path.is_file() or not md_path.read_text(encoding="utf-8").strip():
        c.reason = "problem.md missing or empty"
        return c

    # 2) meta.json valid + has a title (the ONLY field we take from it) -------
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

    # 3) rest/<slug>.json valid JSON -----------------------------------------
    try:
        rest = json.loads(rest_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        c.reason = f"rest/{slug}.json is not valid JSON ({exc})"
        return c

    # `hints` is an OPTIONAL extra the core contract doesn't include, and the
    # structural validator forbids unknown keys — so lift it out before validating
    # the core, then normalize + carry it through (content.write_problem_files /
    # upsert_problem / load_problem_dir all already support hints). Up to 3 are
    # kept (normalize_hints); extras are dropped.
    raw_hints = rest.pop("hints", None)
    if raw_hints is not None and not isinstance(raw_hints, (list, str)):
        c.warnings.append(f"'hints' should be a list of strings (got "
                          f"{type(raw_hints).__name__}); ignored")
        raw_hints = None
    hints = content.normalize_hints(raw_hints)
    if raw_hints and not hints:
        c.warnings.append("'hints' present but empty/blank after cleanup; ignored")
    c.n_hints = len(hints)

    # 4) STRUCTURAL — strict core-contract validation (test_llm_output.py) ----
    rep = tlo.validate(rest, strict=strict)
    if rep.errors:
        c.reason = "structural: " + rep.errors[0]
        c.detail = [f"ERROR: {e}" for e in rep.errors[1:]]
        return c
    if strict and rep.warnings:
        c.reason = "structural (strict): " + rep.warnings[0]
        c.detail = [f"WARN: {w}" for w in rep.warnings[1:]]
        return c
    # Keep test_llm_output's warnings except its blanket "not canonical" tag note:
    # it fires even for aliases that fold cleanly (bfs -> breadth-first-search). We
    # replace it below with the precise "won't fold" signal from unknown_tags.
    c.warnings.extend(w for w in rep.warnings if not w.lstrip().lower().startswith("tags:"))
    c.difficulty = rest.get("difficulty", "?")
    c.compare = rest.get("compare", "?")
    c.n_tests = len(rest.get("tests", []))

    # Surface (but don't block on) tags that are neither canonical nor a known
    # alias — normalize_tags passes these through *unchanged*, so they persist
    # on disk as-is. The owner may want to fold them into the canonical vocab
    # (specs/tags.md) rather than let an invented tag land.
    unk = unknown_tags(rest.get("tags"))
    if unk:
        c.warnings.append(f"non-canonical tag(s) {unk} not in vocabulary — "
                          "will persist as-is (see specs/tags.md)")

    # 5) SLUG COLLISION — never a silent overwrite (docs/problem-generation.md)
    if slug in existing:
        if not allow_overwrite:
            c.reason = ("slug already exists in content/ or DB — possible duplicate; "
                        "skipped (use --overwrite to replace deliberately)")
            return c
        c.overwrites = True

    # 6) BEHAVIORAL + 7) CONSISTENCY — one sandbox run via audit.audit_problem.
    #    Its step 1 IS the authoritative behavioral check (canonical passes all
    #    tests in the real sandbox); steps 2-3 are the statement<->judge audit.
    statement = md_path.read_text(encoding="utf-8")

    # Figures: the statement references images as relative `](assets/<file>)`. On
    # import we copy statements/<slug>/assets/ into content/problems/<slug>/assets/
    # (binary-safe) and rewrite the refs to the served `/problems/<slug>/assets/`
    # URL (see docs/problem-images.md). Warn about any referenced file that's
    # missing (a broken image) — soft, doesn't disqualify.
    refs = re.findall(r"\]\(assets/([^)]+)\)", statement)
    if refs:
        assets_dir = stmt_dir / "assets"
        gone = [r for r in refs if not (assets_dir / r).is_file()]
        if gone:
            c.warnings.append(f"statement references missing asset(s): {sorted(set(gone))}")
        if assets_dir.is_dir() and any(assets_dir.iterdir()):
            c.asset_src = assets_dir

    ns = _problem_ns(rest, statement)
    issues = audit.audit_problem(ns)
    if not ns._canon:  # canonical did NOT pass all its tests
        c.reason = "behavioral: canonical solution fails its own tests"
        c.detail = _behavioral_detail(rest)
        return c
    consistency = [i for i in issues if "pass all its tests" not in i
                   and "no canonical" not in i]
    if consistency:
        c.reason = "consistency: " + consistency[0]
        c.detail = [f"- {i}" for i in consistency[1:]]
        return c

    # Qualified — assemble the durable problem dict for import.
    c.ok = True
    c.data = _problem_dict(slug, title, statement, rest, hints)
    return c


def _problem_ns(rest: dict, statement: str) -> SimpleNamespace:
    """A Problem-like stand-in with exactly the attributes run_submission and
    audit.audit_problem read (mirrors verify_json.grade's SimpleNamespace)."""
    tests = [
        SimpleNamespace(
            name=t.get("name", f"test-{i + 1}"), input=t.get("input", {}),
            expected=t.get("expected"), weight=t.get("weight", 1),
            hidden=t.get("hidden", False),
        )
        for i, t in enumerate(rest.get("tests", []))
    ]
    return SimpleNamespace(
        function_name=rest["function_name"].strip(),
        params=rest.get("params", []),
        return_type=(rest.get("return_type") or "").strip(),
        compare=rest.get("compare", "exact"),
        canonical_solution=rest["canonical_solution"],
        statement_md=statement,
        time_limit_ms=settings.EXEC_TIME_LIMIT_MS,
        memory_limit_mb=settings.EXEC_MEMORY_LIMIT_MB,
        points=100,
        tests=tests,
    )


def _behavioral_detail(rest: dict) -> list[str]:
    """Per-failing-test lines (status / expected / actual) for the report, reusing
    the same grade path as scripts/verify_json.py."""
    lines: list[str] = []
    try:
        g = vj.grade(rest)
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
            exp = rest["tests"][i].get("expected")
            lines.append(f"    expected={json.dumps(exp)}")
            lines.append(f"    actual  ={json.dumps(r.returned)}")
    return lines


def _problem_dict(slug: str, title: str, statement: str, rest: dict,
                  hints: list[str]) -> dict:
    """Combine the three sources into the dict content.write_problem_files wants.
    Title comes from statements/<slug>/meta.json; the statement from problem.md;
    everything load-bearing from rest/<slug>.json; `hints` (already normalized to
    ≤3 clean strings) is carried through when the rest file supplied any. Limits/
    scoring fall to the write_problem_files defaults. Relative image refs are
    rewritten to the served URL so they resolve once the assets/ dir is copied
    alongside (matches import_top150.py / docs/problem-images.md)."""
    statement = statement.replace("](assets/", f"](/problems/{slug}/assets/")
    return {
        "slug": slug,
        "title": title,
        "difficulty": rest["difficulty"],
        "topics": rest["tags"],
        "hints": hints,  # already normalized (≤3); [] when none supplied
        "statement_md": statement,
        "function_name": rest["function_name"],
        "params": rest["params"],
        "return_type": rest["return_type"],
        "compare": rest["compare"],
        "starter_code": rest["starter_code"],
        "canonical_solution": rest["canonical_solution"],
        "tests": rest["tests"],
    }


# ---------------------------------------------------------------------------
# Import: write the durable mirror, reload it, upsert into the DB, re-verify.
# ---------------------------------------------------------------------------
def _copy_assets(c: Candidate) -> None:
    """Copy the statement's binary figures into content/problems/<slug>/assets/.

    write_problem_files' own `assets` map is text-only (SVG); these are jpg/png,
    so we copy the files as bytes (shutil.copy2) — matching import_top150.py."""
    if c.asset_src is None:
        return
    dst = settings.CONTENT_DIR / c.slug / "assets"
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(c.asset_src.iterdir()):
        if f.is_file():
            shutil.copy2(f, dst / f.name)


def import_candidates(cands: list[Candidate]) -> int:
    """Write + seed + re-verify each qualifying candidate. Returns the number that
    round-tripped cleanly (written to disk AND passing all tests from the DB)."""
    init_db()
    imported = 0
    with SessionLocal() as db:
        for c in cands:
            assert c.data is not None
            content.write_problem_files(c.data)                 # durable mirror
            _copy_assets(c)                                     # binary figures, if any
            # Reload from disk so the DB matches exactly what was written (the same
            # path scripts/seed.py uses), then upsert that.
            reloaded = content.load_problem_dir(settings.CONTENT_DIR / c.slug)
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
    print(f"\n{'slug':40} {'status':9} {'diff':7} {'compare':13} {'tests':5} {'hints':5}")
    print("-" * 94)
    for c in sorted(cands, key=lambda x: (not x.ok, x.slug)):
        status = "QUALIFY" if c.ok else "SKIP"
        row = (f"{c.slug:40} {status:9} {c.difficulty:7} {c.compare:13} "
               f"{c.n_tests or '':<5} {c.n_hints or '':<5}")
        if c.overwrites:
            row += "  (overwrites existing)"
        print(row)
        if not c.ok:
            print(f"    ↳ {c.reason}")
        for w in c.warnings:
            print(f"    · warn: {w}")
        if verbose:
            for d in c.detail:
                print(f"      {d}")


def confirm(n: int) -> bool:
    try:
        ans = input(f"\nImport {n} qualifying problem(s) into content/ and the DB? [y/N] ")
    except EOFError:
        print("no TTY for confirmation; re-run with --yes to import non-interactively.")
        return False
    return ans.strip().lower() in ("y", "yes")


def existing_slugs(coll_content_dir: pathlib.Path) -> set[str]:
    """Slugs already in the bank: on disk (content/problems/) OR in the DB. Their
    union is what a new slug must avoid to not risk clobbering a real problem."""
    on_disk = {p.name for p in coll_content_dir.iterdir()
               if p.is_dir() and (p / "meta.json").exists()} if coll_content_dir.is_dir() else set()
    in_db: set[str] = set()
    try:
        init_db()
        with SessionLocal() as db:
            in_db = {row[0] for row in db.query(Problem.slug).all()}
    except Exception as exc:  # noqa: BLE001 - a missing/locked DB shouldn't hide disk collisions
        print(f"note: could not read the DB for collision check ({exc}); "
              "using content/problems/ only.")
    return on_disk | in_db


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirname", type=pathlib.Path,
                    help="collection directory (contains statements/ and rest/)")
    ap.add_argument("-y", "--yes", action="store_true",
                    help="skip the confirmation prompt (import all that qualify)")
    ap.add_argument("--dry-run", action="store_true",
                    help="run every check and report, but never write/import")
    ap.add_argument("--overwrite", action="store_true",
                    help="deliberately replace a problem whose slug already exists "
                         "(default: skip it as a possible duplicate)")
    ap.add_argument("--strict", action="store_true",
                    help="treat structural warnings as disqualifying too")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="print per-test / per-error detail under each skipped row")
    args = ap.parse_args(argv)

    coll = args.dirname
    if not coll.is_dir():
        print(f"error: {coll} is not a directory", file=sys.stderr)
        return 2
    stmt_root, rest_root = coll / "statements", coll / "rest"
    if not stmt_root.is_dir() or not rest_root.is_dir():
        print(f"error: {coll} must contain both 'statements/' and 'rest/' "
              "subdirectories", file=sys.stderr)
        return 2

    # Every slug seen on either side, so orphans on both sides are reported.
    stmt_slugs = {p.name for p in stmt_root.iterdir() if p.is_dir()}
    rest_slugs = {p.stem for p in rest_root.glob("*.json")}
    all_slugs = sorted(stmt_slugs | rest_slugs)
    if not all_slugs:
        print(f"No problems found under {coll} (empty statements/ and rest/).")
        return 0

    existing = existing_slugs(settings.CONTENT_DIR)

    print(f"Validating {len(all_slugs)} slug(s) from {coll} ...")
    cands = [check_slug(s, coll, existing, strict=args.strict,
                        allow_overwrite=args.overwrite) for s in all_slugs]

    print_report(cands, args.verbose)

    qualifying = [c for c in cands if c.ok]
    n_ok, n_skip = len(qualifying), len(cands) - len(qualifying)
    print("\n" + "-" * 88)
    print(f"{len(cands)} slug(s): {n_ok} qualify, {n_skip} skipped.")

    if args.dry_run:
        print("--dry-run: nothing written.")
        return 0 if n_skip == 0 else 1
    if not qualifying:
        print("Nothing to import.")
        return 1 if n_skip else 0
    if not (args.yes or confirm(n_ok)):
        print("Aborted — nothing imported.")
        return 1

    print(f"\nImporting {n_ok} problem(s) ...")
    imported = import_candidates(qualifying)
    print(f"\nDone: {imported}/{n_ok} imported and verified into "
          f"content/problems/ and the DB.")
    if n_skip:
        print(f"({n_skip} slug(s) were skipped — see the report above.)")
    # Non-zero if anything was skipped or an import failed to re-verify, so a CI
    # or scripted caller notices an imperfect run.
    return 0 if (imported == n_ok and n_skip == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
