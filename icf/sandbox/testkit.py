"""Assertions and case registration for ICF test modules.

**Runs inside the sandbox.** Stdlib only, no imports from ``icf`` or ``app``: it
is copied into the run directory as ``icf_testkit.py`` next to the solver's
``solution.py``, and every test module imports it from there.

A test module is a plain Python file that registers cases with :func:`case`::

    from icf_testkit import case, expect

    @case("a field is gone at exactly ts + ttl")
    def ttl_boundary(Database):
        db = Database()
        db.set_with_ttl("1", "A", "BC", "1", "9")
        expect(db.get("10", "A", "BC"), "", "field should have expired")

Each case takes one argument — the class the solver was asked to implement —
and constructs its own instances, so nothing leaks between cases except what
the solver puts in module globals.

Why `expect` rather than bare `assert`: the failure message is what the solver
reads in the results panel, and `assert a == b` gives them nothing. Plain
`assert` still works and is reported as a failure; it is just less useful.
"""
from __future__ import annotations

#: Cases registered by the module currently being imported. The harness drains
#: this between imports, so a case's identity is (module, function name).
_PENDING: list[tuple[str, str, object]] = []

#: How much of a value to show in a failure message before cutting it off. Long
#: enough for a scan string or a small list, short enough to stay readable.
MAX_REPR = 400


class ExpectationFailed(AssertionError):
    """A case's expectation did not hold. Carries the message the solver sees."""


def case(label: str):
    """Register the decorated function as one test case, described by ``label``.

    The label is what a *visible* test shows in the UI, so write it as the
    behaviour being checked ("scan skips expired fields"), not as a test name.
    """
    def decorate(fn):
        _PENDING.append((fn.__name__, label, fn))
        return fn

    return decorate


def drain() -> list[tuple[str, str, object]]:
    """Harness-only: take the cases registered since the last call."""
    taken = list(_PENDING)
    _PENDING.clear()
    return taken


def brief(value: object) -> str:
    """``repr`` with a ceiling, so one huge list can't drown the panel."""
    try:
        text = repr(value)
    except Exception:  # noqa: BLE001 - a solver's __repr__ may raise
        return f"<unreprable {type(value).__name__}>"
    if len(text) <= MAX_REPR:
        return text
    return text[:MAX_REPR] + f"… ({len(text)} chars)"


def expect(actual: object, expected: object, note: str = "") -> None:
    """Assert ``actual == expected``, reporting both values on failure."""
    if actual == expected:
        return
    raise ExpectationFailed(
        f"expected {brief(expected)}, got {brief(actual)}"
        + (f" — {note}" if note else ""))


def expect_true(condition: object, note: str = "") -> None:
    """Assert a condition holds. ``note`` should say what was being checked."""
    if condition:
        return
    raise ExpectationFailed(note or "expected a truthy value, got "
                            + brief(condition))


def expect_close(actual: object, expected: float, tol: float = 1e-9,
                 note: str = "") -> None:
    """Assert two numbers agree within ``tol`` — for the rare float answer."""
    try:
        ok = abs(float(actual) - float(expected)) <= tol  # type: ignore[arg-type]
    except (TypeError, ValueError):
        ok = False
    if ok:
        return
    raise ExpectationFailed(
        f"expected {expected} (±{tol}), got {brief(actual)}"
        + (f" — {note}" if note else ""))


def expect_raises(exc_types, fn, *args, **kwargs) -> BaseException:
    """Assert calling ``fn`` raises one of ``exc_types``; return the exception."""
    names = getattr(exc_types, "__name__", None) or "/".join(
        t.__name__ for t in exc_types)
    try:
        result = fn(*args, **kwargs)
    except exc_types as exc:
        return exc
    except Exception as exc:  # noqa: BLE001 - wrong exception is a failure, not an error
        raise ExpectationFailed(
            f"expected {names}, got {type(exc).__name__}: {exc}") from None
    raise ExpectationFailed(
        f"expected {names}, but the call returned {brief(result)}")
