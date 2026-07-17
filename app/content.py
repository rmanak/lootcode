"""Load problem definitions from content/problems/ into dicts the DB can use.

See specs/problem-schema.md for the on-disk format.
"""
from __future__ import annotations

import json
from pathlib import Path

from .config import settings
from .tags import normalize_tags


#: A problem may carry at most this many hints (shown as "Hint 1..N").
MAX_HINTS = 3


def _read(path: Path) -> str | None:
    return path.read_text(encoding="utf-8") if path.exists() else None


def normalize_hints(raw) -> list[str]:
    """Coerce a meta.json `hints` value into a clean list of at most MAX_HINTS
    non-empty strings. Tolerant of a missing field, `null`, or a lone string."""
    if not raw:
        return []
    if isinstance(raw, str):
        raw = [raw]
    hints = [str(h).strip() for h in raw if str(h).strip()]
    return hints[:MAX_HINTS]


def load_problem_dir(dir_path: Path) -> dict:
    """Parse one content/problems/<slug>/ directory into a problem dict."""
    meta = json.loads((dir_path / "meta.json").read_text(encoding="utf-8"))
    statement = _read(dir_path / "problem.md") or ""
    cases = json.loads((dir_path / "tests" / "cases.json").read_text(encoding="utf-8"))

    # V1 is Python-only; pick the python starter + canonical solution if present.
    starter = _read(dir_path / "starters" / "python" / "solution.py") or ""
    canonical = _read(dir_path / "solution" / "solution.py")

    fn = meta.get("function", {})
    limits = meta.get("limits", {})
    scoring = meta.get("scoring", {})

    # Class-based "design" problems (kind="class") carry a `class` block instead
    # of a `function` block. We reuse `params` for the constructor params and
    # store the method list in `class_methods`; `function_name`/`return_type`
    # stay empty. See specs/problem-schema.md.
    kind = meta.get("kind", "function")
    if kind == "class":
        cls = meta.get("class", {})
        function_name = ""
        params = (cls.get("constructor") or {}).get("params", [])
        return_type = ""
        class_name = cls.get("name", "")
        class_methods = cls.get("methods", [])
    else:
        function_name = fn.get("name", "")
        params = fn.get("params", [])
        return_type = (fn.get("returns") or {}).get("type", "")
        class_name = None
        class_methods = None

    return {
        "slug": meta["slug"],
        "title": meta["title"],
        "difficulty": meta.get("difficulty", "easy"),
        "topics": meta.get("tags", meta.get("topics", [])),
        "hints": normalize_hints(meta.get("hints")),
        "statement_md": statement,
        "kind": kind,
        "function_name": function_name,
        "params": params,
        "return_type": return_type,
        "class_name": class_name,
        "class_methods": class_methods,
        "time_limit_ms": limits.get("timeLimitMs", settings.EXEC_TIME_LIMIT_MS),
        "memory_limit_mb": limits.get("memoryLimitMb", settings.EXEC_MEMORY_LIMIT_MB),
        "scoring_type": scoring.get("type", "weighted"),
        "points": scoring.get("points", 100),
        "compare": meta.get("compare", "exact"),
        "starter_code": starter,
        "canonical_solution": canonical,
        "source": "file",
        "tests": [
            {
                "name": c["name"],
                "input": c["input"],
                "expected": c["expected"],
                "weight": c.get("weight", 1),
                "hidden": c.get("hidden", False),
            }
            for c in cases.get("cases", [])
        ],
    }


def load_all(content_dir: Path | None = None) -> list[dict]:
    base = content_dir or settings.CONTENT_DIR
    if not base.exists():
        return []
    problems = []
    for child in sorted(base.iterdir()):
        if child.is_dir() and (child / "meta.json").exists():
            problems.append(load_problem_dir(child))
    return problems


def load_all_roots(content_dirs: list[Path] | None = None) -> list[dict]:
    """Load problems across every configured content root, in order: the committed
    default set (content/problems/) then the optional, gitignored extended set
    (content/problems-extended/). Missing roots are skipped. This mirrors how
    seeding discovers problems (see `settings.content_dirs`), so bank-wide tooling
    covers the extended set too. Pass an explicit list to override the roots."""
    roots = content_dirs if content_dirs is not None else settings.content_dirs
    problems: list[dict] = []
    for base in roots:
        problems.extend(load_all(base))
    return problems


def load_collections(collections_dir: Path | None = None) -> list[dict]:
    """Parse `content/collections/*.json` into collection dicts.

    Each manifest is `{"slug", "title", "subtitle"?, "problems": [<slug>, ...]}`,
    where the `problems` order is the canonical study order. Returns `[]` if the
    directory is absent so older checkouts (and tests with no collections) are
    unaffected. Files are loaded in sorted name order for deterministic seeding.
    """
    base = collections_dir or settings.COLLECTIONS_DIR
    if not base.exists():
        return []
    collections = []
    for path in sorted(base.glob("*.json")):
        meta = json.loads(path.read_text(encoding="utf-8"))
        collections.append({
            "slug": meta["slug"],
            "title": meta.get("title", meta["slug"]),
            "subtitle": meta.get("subtitle", ""),
            "problems": list(meta.get("problems", [])),
        })
    return collections


def write_problem_files(data: dict, content_dir: Path | None = None) -> Path:
    """Write a problem dict back to the on-disk content format (so manually- and
    AI-created problems are durable and live alongside the seeded ones)."""
    base = (content_dir or settings.CONTENT_DIR) / data["slug"]
    (base / "tests").mkdir(parents=True, exist_ok=True)
    (base / "starters" / "python").mkdir(parents=True, exist_ok=True)
    (base / "solution").mkdir(parents=True, exist_ok=True)

    (base / "problem.md").write_text(data.get("statement_md", ""), encoding="utf-8")
    hints = normalize_hints(data.get("hints"))
    kind = data.get("kind", "function")
    # A class problem writes a `class` block (name + constructor + methods); a
    # function problem writes the `function` block. Exactly one is present.
    if kind == "class":
        contract = {
            "kind": "class",
            "class": {
                "name": data.get("class_name", ""),
                "constructor": {"params": data.get("params", [])},
                "methods": data.get("class_methods") or [],
            },
        }
    else:
        contract = {
            "function": {
                "name": data["function_name"],
                "params": data.get("params", []),
                "returns": {"type": data.get("return_type", "")},
            },
        }
    meta = {
        "slug": data["slug"],
        "title": data["title"],
        "difficulty": data.get("difficulty", "easy"),
        "tags": normalize_tags(data.get("topics", [])),
        # Omitted entirely when there are none, so hint-less problems stay clean.
        **({"hints": hints} if hints else {}),
        "languages": ["python"],
        "limits": {
            "timeLimitMs": data.get("time_limit_ms", settings.EXEC_TIME_LIMIT_MS),
            "memoryLimitMb": data.get("memory_limit_mb", settings.EXEC_MEMORY_LIMIT_MB),
        },
        **contract,
        "scoring": {
            "type": data.get("scoring_type", "weighted"),
            "points": data.get("points", 100),
        },
        "compare": data.get("compare", "exact"),
    }
    (base / "meta.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    cases = {"cases": [
        {"name": t["name"], "input": t["input"], "expected": t["expected"],
         "weight": t.get("weight", 1), "hidden": t.get("hidden", False)}
        for t in data.get("tests", [])
    ]}
    (base / "tests" / "cases.json").write_text(
        json.dumps(cases, indent=2) + "\n", encoding="utf-8")
    (base / "starters" / "python" / "solution.py").write_text(
        data.get("starter_code", "") or "", encoding="utf-8")
    if data.get("canonical_solution"):
        (base / "solution" / "solution.py").write_text(
            data["canonical_solution"], encoding="utf-8")

    # Figures (SVG text), served by /problems/<slug>/assets/<file>. See
    # docs/problem-images.md. Each value is the file's text content.
    assets = data.get("assets") or {}
    if assets:
        (base / "assets").mkdir(parents=True, exist_ok=True)
        for fname, text in assets.items():
            (base / "assets" / fname).write_text(text, encoding="utf-8")
    return base
