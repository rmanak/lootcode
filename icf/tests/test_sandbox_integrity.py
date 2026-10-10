"""What untrusted code must *not* be able to do.

Each test here is a submission written to attack the grader rather than to
solve the problem. They exist because a security review found the first two
working against an earlier version of this harness: a six-line solution scored
100%, and a three-line one printed the hidden tests into its own results.

See ``icf/docs/security.md`` and ``docs/adr/0003-icf-grading-runs-two-processes.md``.
"""
from __future__ import annotations

import pytest

from icf import runner

pytestmark = pytest.mark.slow


def _cases(graded):
    return [c for lv in graded.levels for c in lv.cases]


FORGE_RESULTS = '''
import json, os

# Claim every case passed, then leave before the real run can happen.
try:
    payload = json.load(open("payload.json"))
    cases = payload["cases"]
except Exception:
    cases = []
json.dump({"load_error": None,
           "results": [{"id": c["id"], "status": "passed", "message": None,
                        "time_ms": 1, "stdout": ""} for c in cases]},
          open("result.json", "w"))
os._exit(0)


class Counter:
    pass
'''


def test_a_solution_cannot_write_its_own_results_file(toy):
    """The process that writes result.json never runs the solution."""
    graded = runner.grade(toy, FORGE_RESULTS, [1, 2, 3, 4])
    assert not graded.all_passed
    assert graded.passed_count == 0, "a forged result.json must count for nothing"
    assert graded.total_count == 8, "every case is still accounted for"
    assert all(c.status in ("error", "timeout") for c in _cases(graded))


READ_THE_TESTS = '''
import os


class Counter:
    def __init__(self):
        listing = sorted(os.listdir("."))
        print("FILES:" + ",".join(listing))
        for name in listing:
            if "test" in name and name.endswith(".py"):
                try:
                    print("SOURCE:" + open(name).read())
                except OSError as exc:
                    print("DENIED:" + str(exc))
        self._values = []

    def add(self, n):
        self._values.append(n)
        return len(self._values)

    def total(self):
        return sum(self._values)

    def undo(self):
        if not self._values:
            return False
        self._values.pop()
        return True

    def label(self):
        return "+".join(str(v) for v in self._values)
'''


def test_a_solution_cannot_read_the_tests_that_grade_it(toy):
    """Test sources are deleted before the solution is ever imported."""
    graded = runner.grade(toy, READ_THE_TESTS, [1, 2, 3, 4])
    assert graded.all_passed, "the solution itself is correct; only the snooping fails"

    printed = "\n".join(c.stdout for c in _cases(graded))
    assert "FILES:" in printed, "the probe really did run"
    # Neither the sources nor their compiled copies: `python -I` ignores
    # PYTHONDONTWRITEBYTECODE, so a .pyc of a test module used to survive in
    # __pycache__ carrying every expected value as a string constant.
    assert "icf_tests" not in printed, f"a test module was still readable: {printed}"
    assert "__pycache__" not in printed
    # The labels of this problem's own cases must not appear either.
    assert "adding many values keeps counting" not in printed
    assert "solution.py" in printed, "the probe could see its own file"


def test_hidden_cases_carry_no_message_or_output_even_before_the_api(toy):
    """Redaction is in the runner, not only in the JSON view."""
    graded = runner.grade(toy, READ_THE_TESTS, [1, 2, 3, 4])
    hidden = [c for c in _cases(graded) if c.hidden]
    assert hidden
    assert all(c.message is None and c.stdout == "" for c in hidden)

    visible = [c for c in _cases(graded) if not c.hidden]
    assert any(c.stdout for c in visible), "visible cases still report output"


HUGE_MESSAGE = '''
class Counter:
    def __init__(self):
        self._values = []

    def add(self, n):
        raise AssertionError("A" * 3_000_000)

    def total(self):
        return 0

    def undo(self):
        return False

    def label(self):
        return ""
'''


def test_an_enormous_failure_message_cannot_wipe_out_the_run(toy):
    """A three-megabyte assertion used to blow the file-size rlimit and lose
    every result, including the cases that had already passed."""
    graded = runner.grade(toy, HUGE_MESSAGE, [1, 2])
    cases = _cases(graded)
    assert len(cases) == 4
    failed = [c for c in cases if c.status == "failed"]
    assert failed, "the assertion is still reported as a failure"
    assert all(len(c.message or "") < 5000 for c in cases), "messages are clipped"


DIE_HALFWAY = '''
import os

_seen = []


class Counter:
    def __init__(self):
        _seen.append(1)
        if len(_seen) > 1:
            os._exit(0)          # walk out mid-suite
        self._values = []

    def add(self, n):
        self._values.append(n)
        return len(self._values)

    def total(self):
        return sum(self._values)

    def undo(self):
        return bool(self._values) and (self._values.pop() or True)

    def label(self):
        return "+".join(str(v) for v in self._values)
'''


def test_a_worker_that_walks_out_leaves_the_rest_failed_not_passed(toy):
    """Fail closed: a verdict has to arrive from the worker to count."""
    graded = runner.grade(toy, DIE_HALFWAY, [1, 2, 3, 4])
    assert not graded.all_passed
    unreported = [c for c in _cases(graded) if c.status in ("error", "timeout")]
    assert unreported, "the cases after the exit are marked, not assumed"
    assert graded.passed_count < graded.total_count


def test_the_canonical_still_passes_through_all_of_this(toy):
    """The guard rails must not change what a correct solution scores."""
    graded = runner.grade(toy, toy.canonical_code, [1, 2, 3, 4])
    assert graded.all_passed, graded
    assert graded.passed_count == 8
