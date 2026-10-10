"""Load ICF problems from disk, and check that one is well-formed.

Problems live in ``icf/problems/<slug>/`` (see ``icf/docs/problem-format.md``)
and are read straight off disk into memory — there is no seeding step and no
copy in the database, because a handful of definitions do not need one and a
second copy is a second thing to drift.

Nothing here executes problem code. The case list for a level is recovered by
**parsing** the test module with ``ast`` and looking for ``@case("…")``
decorators, the same static-only stance ``app/problem_spec.py`` takes.
"""
from __future__ import annotations

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from .config import settings

LEVELS = (1, 2, 3, 4)
VISIBILITIES = ("visible", "hidden")

#: `/icf/static` is a mount, so a problem may not claim that slug.
RESERVED_SLUGS = frozenset({"static", "attempts", "api"})
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class ContentError(Exception):
    """A problem directory is malformed in a way that stops it loading at all."""


@dataclass(frozen=True)
class CaseSpec:
    """One authored test case, as discovered statically in a test module."""

    level: int
    hidden: bool
    module: str        # sandbox module name, e.g. "icf_tests_l1_visible"
    func: str          # the decorated function's name
    label: str         # human-readable description from @case("…")

    @property
    def id(self) -> str:
        return f"L{self.level}:{'hidden' if self.hidden else 'visible'}:{self.func}"


@dataclass(frozen=True)
class Level:
    number: int
    title: str
    points: int
    statement_md: str
    methods: tuple[str, ...]
    cases: tuple[CaseSpec, ...]

    @property
    def visible_cases(self) -> tuple[CaseSpec, ...]:
        return tuple(c for c in self.cases if not c.hidden)

    @property
    def hidden_cases(self) -> tuple[CaseSpec, ...]:
        return tuple(c for c in self.cases if c.hidden)


@dataclass(frozen=True)
class Problem:
    slug: str
    title: str
    difficulty: str
    blurb: str
    tags: tuple[str, ...]
    class_name: str
    time_cap_minutes: int
    case_time_limit_ms: int
    intro_md: str
    starter_code: str
    canonical_code: str
    levels: tuple[Level, ...]
    #: level -> the canonical as it stood at the end of that level, when the
    #: author supplied one. Used by the verifier to prove a level adds work.
    checkpoints: dict[int, str] = field(default_factory=dict)
    #: module name -> source, ready to be written into a sandbox run directory.
    test_sources: dict[str, str] = field(default_factory=dict)
    path: Path = Path()

    def level(self, number: int) -> Level:
        for lv in self.levels:
            if lv.number == number:
                return lv
        raise KeyError(number)

    @property
    def total_points(self) -> int:
        return sum(lv.points for lv in self.levels)

    @property
    def case_count(self) -> int:
        return sum(len(lv.cases) for lv in self.levels)

    def cases_for(self, levels, include_hidden: bool) -> list[CaseSpec]:
        """Every case for ``levels``, in level then authored order."""
        out: list[CaseSpec] = []
        for number in sorted(levels):
            for c in self.level(number).cases:
                if include_hidden or not c.hidden:
                    out.append(c)
        return out


def module_name(level: int, hidden: bool) -> str:
    return f"icf_tests_l{level}_{'hidden' if hidden else 'visible'}"


def parse_cases(source: str, level: int, hidden: bool, where: str) -> list[CaseSpec]:
    """Find every ``@case("label")``-decorated function, statically.

    Order is source order, which is the order the UI lists them in — so an
    author can put the simplest case first and it stays first.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise ContentError(f"{where}: {exc}") from exc

    found: list[CaseSpec] = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            # A bare `@case` (no label) registers nothing and fails silently at
            # import time, so it is called out here rather than quietly dropped.
            if isinstance(dec, ast.Name) and dec.id == "case":
                raise ContentError(
                    f"{where}: @case on `{node.name}` needs a label — "
                    'write @case("what this checks")')
            if not (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name)
                    and dec.func.id == "case"):
                continue
            if not (dec.args and isinstance(dec.args[0], ast.Constant)
                    and isinstance(dec.args[0].value, str)):
                raise ContentError(
                    f"{where}: @case on `{node.name}` needs a string label")
            found.append(CaseSpec(level=level, hidden=hidden,
                                  module=module_name(level, hidden),
                                  func=node.name, label=dec.args[0].value))
    return found


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_problem(directory: Path) -> Problem:
    """Read one ``<slug>/`` directory. Raises :class:`ContentError` if it is not
    a loadable problem; *quality* checks live in :func:`validate`."""
    meta_path = directory / "meta.json"
    if not meta_path.is_file():
        raise ContentError(f"{directory}: no meta.json")
    try:
        meta = json.loads(_read(meta_path))
    except ValueError as exc:
        raise ContentError(f"{meta_path}: {exc}") from exc

    slug = meta.get("slug") or directory.name
    levels: list[Level] = []
    test_sources: dict[str, str] = {}

    for spec in meta.get("levels", []):
        number = spec.get("level")
        if number not in LEVELS:
            raise ContentError(f"{slug}: level {number!r} is not one of {LEVELS}")
        statement = directory / "levels" / f"level{number}.md"
        if not statement.is_file():
            raise ContentError(f"{slug}: missing levels/level{number}.md")
        cases: list[CaseSpec] = []
        for visibility in VISIBILITIES:
            test_file = directory / "tests" / f"level{number}" / f"{visibility}.py"
            if not test_file.is_file():
                continue
            source = _read(test_file)
            name = module_name(number, visibility == "hidden")
            test_sources[name] = source
            cases.extend(parse_cases(source, number, visibility == "hidden",
                                     f"{slug}/tests/level{number}/{visibility}.py"))
        levels.append(Level(
            number=number,
            title=spec.get("title", f"Level {number}"),
            points=int(spec.get("points", 25)),
            statement_md=_read(statement),
            methods=tuple(spec.get("methods", [])),
            cases=tuple(cases),
        ))

    starter = directory / "starter" / "solution.py"
    canonical = directory / "solution" / "solution.py"
    checkpoints = {}
    for number in LEVELS:
        checkpoint = directory / "solution" / f"level{number}.py"
        if checkpoint.is_file():
            checkpoints[number] = _read(checkpoint)

    return Problem(
        slug=slug,
        title=meta.get("title", slug),
        difficulty=meta.get("difficulty", "medium"),
        blurb=meta.get("blurb", ""),
        tags=tuple(meta.get("tags", [])),
        class_name=meta.get("class_name", ""),
        time_cap_minutes=int(meta.get("time_cap_minutes",
                                      settings.DEFAULT_TIME_CAP_MINUTES)),
        case_time_limit_ms=int(meta.get("case_time_limit_ms",
                                        settings.CASE_TIME_LIMIT_MS)),
        intro_md=_read(directory / "problem.md")
        if (directory / "problem.md").is_file() else "",
        starter_code=_read(starter) if starter.is_file() else "",
        canonical_code=_read(canonical) if canonical.is_file() else "",
        levels=tuple(sorted(levels, key=lambda lv: lv.number)),
        checkpoints=checkpoints,
        test_sources=test_sources,
        path=directory,
    )


# --- the spec: what makes a problem fit to serve ---------------------------

def _declared_methods(source: str, class_name: str) -> set[str] | None:
    """Method names defined on ``class_name`` in ``source``; None if absent."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return {n.name for n in node.body
                    if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)}
    return None


def _method_name(signature: str) -> str:
    """The method name out of a declared signature.

    Authors write the signature the way it appears in the starter — either
    ``"def set(self, timestamp, ...) -> None: ..."`` or the bare
    ``"set(timestamp, ...)"`` — so both shapes have to reduce to ``"set"``.
    """
    head = signature.split("(", 1)[0].strip()
    if head.startswith("def "):
        head = head[4:].strip()
    return head


def validate(problem: Problem) -> list[str]:
    """Everything wrong with ``problem`` that can be found without running it.

    Returns a list of human-readable problems; empty means it is servable. The
    behavioural half — the canonical actually passing — is
    ``icf/scripts/verify_icf.py``, which needs the sandbox.
    """
    errors: list[str] = []
    if not SLUG_RE.match(problem.slug):
        errors.append(f"slug {problem.slug!r} must be lower-case-kebab")
    if problem.slug in RESERVED_SLUGS:
        errors.append(f"slug {problem.slug!r} is reserved by a route or mount")
    if not problem.title.strip():
        errors.append("meta.json: title is empty")
    if problem.difficulty not in ("easy", "medium", "hard"):
        errors.append(f"difficulty {problem.difficulty!r} is not easy/medium/hard")
    if not problem.class_name.isidentifier():
        errors.append(f"class_name {problem.class_name!r} is not an identifier")
    if not problem.intro_md.strip():
        errors.append("problem.md is missing or empty")
    if problem.time_cap_minutes <= 0:
        errors.append("time_cap_minutes must be positive")

    numbers = [lv.number for lv in problem.levels]
    if numbers != list(LEVELS):
        errors.append(f"levels must be exactly 1,2,3,4 — found {numbers}")

    declared = _declared_methods(problem.starter_code, problem.class_name)
    if declared is None:
        errors.append(
            f"starter/solution.py does not define a class {problem.class_name}")
    if not problem.canonical_code.strip():
        errors.append("solution/solution.py is missing or empty")
    elif _declared_methods(problem.canonical_code, problem.class_name) is None:
        errors.append(
            f"solution/solution.py does not define a class {problem.class_name}")

    for lv in problem.levels:
        if not lv.statement_md.strip():
            errors.append(f"level {lv.number}: statement is empty")
        if not lv.methods:
            errors.append(f"level {lv.number}: meta.json lists no methods")
        if not lv.visible_cases:
            errors.append(f"level {lv.number}: no visible test cases")
        if declared is not None:
            missing = [m for m in (_method_name(s) for s in lv.methods)
                       if m not in declared]
            if missing:
                errors.append(
                    f"level {lv.number}: starter/solution.py is missing "
                    f"{', '.join(missing)}")
        seen: set[str] = set()
        for c in lv.cases:
            if c.func in seen:
                errors.append(f"level {lv.number}: two cases named {c.func}")
            seen.add(c.func)

    return errors


# --- loading the set -------------------------------------------------------

#: (root, slug) -> (newest mtime seen, parsed problem). Keyed by root as well
#: as slug so pointing ICF_PROBLEMS_DIR somewhere else (a test, a second bank)
#: cannot be served a problem parsed from the other root.
_CACHE: dict[tuple[str, str], tuple[float, Problem]] = {}


def _signature(directory: Path) -> float:
    """Newest mtime under ``directory`` — cheap enough for a few problems, and
    it means an edit shows up on the next request without a restart."""
    newest = directory.stat().st_mtime
    for path in directory.rglob("*"):
        if path.is_file():
            newest = max(newest, path.stat().st_mtime)
    return newest


def load(slug: str, root: Path | None = None) -> Problem | None:
    """One problem by slug, from the mtime-keyed cache."""
    root = root or settings.PROBLEMS_DIR
    directory = root / slug
    if not SLUG_RE.match(slug) or not (directory / "meta.json").is_file():
        return None
    stamp = _signature(directory)
    cache_key = (str(root), slug)
    cached = _CACHE.get(cache_key)
    if cached and cached[0] == stamp:
        return cached[1]
    problem = load_problem(directory)
    _CACHE[cache_key] = (stamp, problem)
    return problem


def load_all(root: Path | None = None) -> list[Problem]:
    """Every loadable problem, ordered by difficulty then title."""
    root = root or settings.PROBLEMS_DIR
    if not root.is_dir():
        return []
    order = {"easy": 0, "medium": 1, "hard": 2}
    found = []
    for directory in sorted(root.iterdir()):
        if not (directory / "meta.json").is_file():
            continue
        problem = load(directory.name, root)
        if problem is not None:
            found.append(problem)
    return sorted(found, key=lambda p: (order.get(p.difficulty, 9), p.title))


def clear_cache() -> None:
    _CACHE.clear()
