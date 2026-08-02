#!/usr/bin/env python3
"""Retire a problem from the bank: on-disk content, collection manifests, and DB.

Removing a problem touches more than its `content/problems*/<slug>/` directory.
The slug is also referenced by name in `content/collections/*.json`, and the DB
holds a `problems` row plus everything hanging off its id — test cases, curated
collection memberships, and **user data** (submissions, their per-test results,
"known" and "visit later" marks). Deleting only the directory leaves the problem
live in the app; deleting only the row leaves dangling references. This does all
of it in one pass, in the right order, and re-seeds collections afterwards so the
study-order positions stay contiguous.

Two situations, one command:

  * **Retire** a problem outright — it can't be judged, it's broken, it's junk::

        python scripts/remove_problem.py random-pick-with-weight

  * **Deduplicate** — the problem is a twin of one already in the bank. Give the
    survivor and every collection that referenced the loser points at the winner
    **in the loser's position**, instead of silently getting shorter::

        python scripts/remove_problem.py two-sum-ii=two-sum

    If a list already contains the survivor, the reference is dropped rather
    than duplicated (a curated list must not name the same problem twice).

`old=new` and `old->new` are both accepted, on the command line or in a
`--from-file` list (one per line, `#` comments allowed), so a batch of dupes can
be retired in a single run.

**User data.** Submissions against a removed problem are DELETED by default, and
the report says how many and whose before anything is written. `--migrate-
submissions` instead repoints them at the replacement — reasonable for true
duplicates, but note the scores were computed against the *removed* problem's
tests, so a migrated submission's pass count may not reflect the survivor's
suite. The database is backed up first either way (see `--backup-dir`).

Nothing is written until every slug resolves and (unless `--yes`) you confirm.
`--dry-run` reports and stops.

Exit codes: 0 removed (or nothing to do), 1 error / aborted.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

#: Tables keyed by `problem_id` that are pure derived/bookkeeping rows: deleting
#: them costs nothing that isn't rebuilt by seeding or simply gone with the
#: problem. `submissions` is deliberately NOT here — it is user data and is
#: handled explicitly (deleted with a loud report, or migrated).
CHILD_TABLES = ("collection_problems", "known_problems", "visit_later_problems",
                "test_cases")

#: Of those, the ones carrying a UNIQUE(user_id, problem_id) — migrating a row
#: onto a problem the user already marked would violate it, so those collapse.
USER_MARK_TABLES = ("known_problems", "visit_later_problems")


@dataclass
class Removal:
    """One slug to remove, and what removing it will cost."""
    slug: str
    replacement: str | None = None
    content_dir: Path | None = None
    problem_id: int | None = None
    test_cases: int = 0
    submissions: int = 0
    submitters: dict[str, int] = field(default_factory=dict)
    test_results: int = 0
    user_marks: int = 0
    collections: dict[str, str] = field(default_factory=dict)  # coll slug -> action
    errors: list[str] = field(default_factory=list)

    @property
    def known(self) -> bool:
        """Does this slug exist at all — on disk or in the database?"""
        return self.content_dir is not None or self.problem_id is not None


def parse_spec(spec: str) -> tuple[str, str | None]:
    """Parse `slug`, `slug=replacement` or `slug->replacement`."""
    for sep in ("->", "="):
        if sep in spec:
            old, _, new = spec.partition(sep)
            old, new = old.strip(), new.strip()
            if not old or not new:
                raise ValueError(f"malformed spec {spec!r} (expected old{sep}new)")
            return old, new
    return spec.strip(), None


def read_specs(path: Path) -> list[str]:
    specs = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            specs.append(line)
    return specs


def find_content_dir(slug: str) -> Path | None:
    """Which content root holds this slug, if any (default or extended)."""
    for root in settings.content_dirs:
        if (root / slug / "meta.json").exists():
            return root / slug
    return None


def collection_files() -> list[Path]:
    base = settings.COLLECTIONS_DIR
    return sorted(base.glob("*.json")) if base.exists() else []


def backup_db(db_path: Path, backup_dir: Path) -> Path:
    """Snapshot the database via SQLite's backup API.

    Not `cp`: the dev server may be running, and a hot file copy of a WAL
    database can catch it mid-transaction. The backup API takes a consistent
    snapshot of a live database, WAL folded in, into a single file.
    """
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = backup_dir / f"{db_path.stem}.bak-{stamp}.db"
    src = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    out = sqlite3.connect(dest)
    try:
        src.backup(out)
    finally:
        out.close()
        src.close()
    return dest


def survey(conn: sqlite3.Connection, removals: list[Removal]) -> None:
    """Fill in what exists on disk and in the DB, and validate every slug."""
    targets = {r.slug for r in removals}
    for r in removals:
        if not SLUG_RE.match(r.slug):
            r.errors.append(f"{r.slug!r} is not a valid slug")
            continue
        r.content_dir = find_content_dir(r.slug)
        row = conn.execute("SELECT id FROM problems WHERE slug = ?", (r.slug,)).fetchone()
        r.problem_id = row[0] if row else None

        if not r.known:
            r.errors.append(f"{r.slug!r} is not in the bank (no content dir, no DB row)")

        if r.replacement:
            if r.replacement == r.slug:
                r.errors.append(f"{r.slug!r} cannot replace itself")
            elif r.replacement in targets:
                r.errors.append(
                    f"replacement {r.replacement!r} is itself being removed")
            elif not find_content_dir(r.replacement) and not conn.execute(
                    "SELECT 1 FROM problems WHERE slug = ?", (r.replacement,)).fetchone():
                r.errors.append(f"replacement {r.replacement!r} is not in the bank")

        if r.problem_id is not None:
            pid = (r.problem_id,)
            r.test_cases = conn.execute(
                "SELECT count(*) FROM test_cases WHERE problem_id = ?", pid).fetchone()[0]
            r.submissions = conn.execute(
                "SELECT count(*) FROM submissions WHERE problem_id = ?", pid).fetchone()[0]
            # LEFT JOIN + COALESCE: identity is cookie-based, so a submission can
            # belong to an anonymous visitor with no username (or, in old rows, to
            # a user since deleted). Those still count as data being destroyed.
            r.submitters = dict(conn.execute(
                "SELECT COALESCE(u.username, '(anonymous)'), count(*) FROM submissions s "
                "LEFT JOIN users u ON u.id = s.user_id WHERE s.problem_id = ? "
                "GROUP BY 1 ORDER BY 2 DESC", pid).fetchall())
            r.test_results = conn.execute(
                "SELECT count(*) FROM test_results WHERE submission_id IN "
                "(SELECT id FROM submissions WHERE problem_id = ?)", pid).fetchone()[0]
            # noqa S608 (here and below): the only thing interpolated into these
            # statements is a table name from the module-level tuples above.
            # Every value is bound. Table names cannot be parameterised in SQL.
            r.user_marks = sum(
                conn.execute(f"SELECT count(*) FROM {t} WHERE problem_id = ?",  # noqa: S608
                             pid).fetchone()[0]
                for t in USER_MARK_TABLES)

        # Collection manifests are the source of truth for membership; the DB
        # rows are rebuilt from them by seeding.
        for path in collection_files():
            meta = json.loads(path.read_text(encoding="utf-8"))
            problems = meta.get("problems", [])
            if r.slug not in problems:
                continue
            if not r.replacement:
                r.collections[meta["slug"]] = "drop"
            elif r.replacement in problems:
                r.collections[meta["slug"]] = f"drop (already has {r.replacement})"
            else:
                r.collections[meta["slug"]] = f"-> {r.replacement}"


def rewrite_collections(removals: list[Removal], verbose: bool) -> list[str]:
    """Replace or drop each slug in every manifest that names it.

    A replacement takes the removed slug's **position**, preserving the curated
    study order. If the manifest already names the replacement, the reference is
    dropped instead — a list must not name the same problem twice.
    """
    mapping = {r.slug: r.replacement for r in removals}
    changed = []
    for path in collection_files():
        meta = json.loads(path.read_text(encoding="utf-8"))
        problems = list(meta.get("problems", []))
        if not any(s in problems for s in mapping):
            continue
        before = len(problems)
        out: list[str] = []
        for slug in problems:
            if slug not in mapping:
                out.append(slug)
                continue
            replacement = mapping[slug]
            if replacement and replacement not in out and replacement not in problems:
                out.append(replacement)
        meta["problems"] = out
        if before != len(out):
            meta["subtitle"] = _restate_count(meta.get("subtitle", ""), before, len(out))
        path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        changed.append(f"{meta['slug']}: {before} -> {len(out)}")
        if verbose:
            print(f"  rewrote {path.name}: {before} -> {len(out)} problems")
    return changed


def _restate_count(subtitle: str, old: int, new: int) -> str:
    """Update a subtitle that states the list's size ("A curated set of 196
    problems"). Only an integer equal to the *old count* is touched, so an
    unrelated number in the same sentence ("the full 500-problem list") survives.
    """
    return re.sub(rf"\b{old}\b", str(new), subtitle) if old != new else subtitle


def apply_db(conn: sqlite3.Connection, removals: list[Removal],
             migrate_submissions: bool, verbose: bool) -> dict[str, int]:
    """Delete (or migrate) every DB row belonging to the removed problems."""
    totals: dict[str, int] = {}

    def bump(table: str, n: int) -> None:
        if n:
            totals[table] = totals.get(table, 0) + n

    for r in removals:
        if r.problem_id is None:
            continue
        pid = r.problem_id
        new_id = None
        if r.replacement:
            row = conn.execute("SELECT id FROM problems WHERE slug = ?",
                               (r.replacement,)).fetchone()
            new_id = row[0] if row else None

        if migrate_submissions and new_id is not None:
            bump("submissions migrated", conn.execute(
                "UPDATE submissions SET problem_id = ? WHERE problem_id = ?",
                (new_id, pid)).rowcount)
            # Marks are (user, problem)-unique: move only where the user hasn't
            # already marked the survivor, drop the rest as redundant.
            for table in USER_MARK_TABLES:
                bump(f"{table} migrated", conn.execute(
                    f"UPDATE {table} SET problem_id = ? WHERE problem_id = ? AND user_id "  # noqa: S608
                    f"NOT IN (SELECT user_id FROM {table} WHERE problem_id = ?)",
                    (new_id, pid, new_id)).rowcount)
        else:
            bump("test_results", conn.execute(
                "DELETE FROM test_results WHERE submission_id IN "
                "(SELECT id FROM submissions WHERE problem_id = ?)", (pid,)).rowcount)
            bump("submissions", conn.execute(
                "DELETE FROM submissions WHERE problem_id = ?", (pid,)).rowcount)

        for table in CHILD_TABLES:
            bump(table, conn.execute(
                f"DELETE FROM {table} WHERE problem_id = ?", (pid,)).rowcount)  # noqa: S608
        bump("problems", conn.execute(
            "DELETE FROM problems WHERE id = ?", (pid,)).rowcount)
        if verbose:
            print(f"  purged DB rows for {r.slug} (id={pid})")
    return totals


def reseed_collections() -> tuple[int, list[str]]:
    """Rebuild collection membership from the manifests.

    Removing a member leaves a hole in the stored `position` sequence; seeding
    rewrites the rows in manifest order, which closes it.
    """
    from app.db import SessionLocal
    from app.store import seed_collections
    db = SessionLocal()
    try:
        return seed_collections(db)
    finally:
        db.close()


def report(removals: list[Removal], migrate: bool) -> None:
    for r in removals:
        head = r.slug if not r.replacement else f"{r.slug}  ->  {r.replacement}"
        print(f"\n  {head}")
        print(f"    content dir : {r.content_dir or '(none)'}")
        print(f"    db row      : "
              f"{f'id={r.problem_id}, {r.test_cases} test case(s)' if r.problem_id else '(none)'}")
        if r.submissions:
            who = ", ".join(f"{u} x{n}" for u, n in r.submitters.items())
            verb = (f"MIGRATE to {r.replacement}" if migrate and r.replacement
                    else "DELETE")
            print(f"    submissions : {verb} {r.submissions} ({who})"
                  f"{'' if migrate and r.replacement else f' + {r.test_results} test result(s)'}")
        if r.user_marks:
            print(f"    user marks  : {r.user_marks} known/visit-later row(s)")
        if r.collections:
            for coll, action in r.collections.items():
                print(f"    collection  : {coll} {action}")
        for err in r.errors:
            print(f"    ERROR       : {err}")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Remove problems from the bank (content, collections, DB).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Specs are `slug`, `slug=replacement` or `slug->replacement`.\n"
               "A replacement inherits the removed slug's place in every collection.",
    )
    ap.add_argument("specs", nargs="*", metavar="SLUG[=REPLACEMENT]")
    ap.add_argument("--from-file", type=Path,
                    help="file of specs, one per line ('#' comments allowed)")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what would change and exit without writing")
    ap.add_argument("-y", "--yes", action="store_true", help="skip the confirmation")
    ap.add_argument("--migrate-submissions", action="store_true",
                    help="repoint submissions at the replacement instead of deleting "
                         "them (requires a replacement; scores were graded against "
                         "the REMOVED problem's tests)")
    ap.add_argument("--backup-dir", type=Path, default=Path("scratchpad/db-backups"),
                    help="where to snapshot the DB first (default: %(default)s)")
    ap.add_argument("--no-backup", action="store_true",
                    help="skip the database snapshot (not recommended)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    specs = list(args.specs)
    if args.from_file:
        if not args.from_file.exists():
            print(f"error: no such file: {args.from_file}", file=sys.stderr)
            return 1
        specs += read_specs(args.from_file)
    if not specs:
        ap.error("give at least one slug, or --from-file")

    removals: list[Removal] = []
    seen: set[str] = set()
    for spec in specs:
        try:
            slug, replacement = parse_spec(spec)
        except ValueError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        if slug in seen:
            print(f"error: {slug!r} listed twice", file=sys.stderr)
            return 1
        seen.add(slug)
        removals.append(Removal(slug=slug, replacement=replacement))

    db_path = Path(settings.DB_PATH)
    if not db_path.exists():
        print(f"error: no database at {db_path}", file=sys.stderr)
        return 1

    conn = sqlite3.connect(db_path, timeout=30)
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        survey(conn, removals)
        print(f"Removing {len(removals)} problem(s) from the bank:")
        report(removals, args.migrate_submissions)

        errors = [e for r in removals for e in r.errors]
        if errors:
            print(f"\nAborted: {len(errors)} problem(s) with errors — nothing written.")
            return 1
        if args.migrate_submissions and not all(r.replacement for r in removals):
            print("\nAborted: --migrate-submissions needs every slug to have a "
                  "replacement.")
            return 1

        total_subs = sum(r.submissions for r in removals)
        if args.dry_run:
            print("\nDry run — nothing written.")
            return 0
        if not args.yes:
            if total_subs and not args.migrate_submissions:
                print(f"\n!! {total_subs} submission(s) will be permanently deleted.")
            reply = input("\nProceed? [y/N] ").strip().lower()
            if reply not in ("y", "yes"):
                print("Aborted — nothing written.")
                return 1

        if not args.no_backup:
            dest = backup_db(db_path, args.backup_dir)
            print(f"\nDatabase backed up -> {dest} "
                  f"({dest.stat().st_size // 1024 // 1024} MB)")

        with conn:
            totals = apply_db(conn, removals, args.migrate_submissions, args.verbose)
        print("DB rows: " + (", ".join(f"{k} {v}" for k, v in totals.items()) or "none"))

        changed = rewrite_collections(removals, args.verbose)
        print("Collections rewritten: " + (", ".join(changed) or "none"))

        for r in removals:
            if r.content_dir and r.content_dir.exists():
                shutil.rmtree(r.content_dir)
                print(f"Deleted {r.content_dir}")

        count, unresolved = reseed_collections()
        print(f"Re-seeded {count} collection(s)"
              + (f" ({len(unresolved)} unresolved slug(s))" if unresolved else ""))

        check = conn.execute("PRAGMA quick_check").fetchone()[0]
        orphans = conn.execute(
            "SELECT count(*) FROM submissions s LEFT JOIN problems p "
            "ON p.id = s.problem_id WHERE p.id IS NULL").fetchone()[0]
        print(f"\nquick_check: {check}; orphaned submissions: {orphans}")
        if check != "ok" or orphans:
            print("WARNING: database did not come out clean — see docs/database.md")
            return 1
        print("Done. Run `make check` to re-verify the bank.")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
