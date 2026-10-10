"""The grader, against real sandbox subprocesses.

Marked ``slow`` like core's executor tier: every test here spawns a process.
What is being pinned is how a *broken* submission is reported, because that is
what a solver sees most often and what silently regresses.
"""
from __future__ import annotations

import shutil
import subprocess

import pytest

from app.config import settings as core_settings
from icf import runner

pytestmark = pytest.mark.slow

BROKEN_TOTAL = '''class Counter:
    def __init__(self):
        self._values = []

    def add(self, n):
        self._values.append(n)
        return len(self._values)

    def total(self):
        return 0

    def undo(self):
        return bool(self._values) and (self._values.pop() or True)

    def label(self):
        return "+".join(str(v) for v in self._values)
'''


def test_the_canonical_passes_every_level(toy):
    graded = runner.grade(toy, toy.canonical_code, [1, 2, 3, 4])
    assert graded.all_passed, graded
    assert graded.total_count == 8
    assert [lv.level for lv in graded.levels] == [1, 2, 3, 4]


def test_a_run_can_exclude_hidden_cases(toy):
    graded = runner.grade(toy, toy.canonical_code, [1], include_hidden=False)
    assert graded.total_count == 1
    assert all(not c.hidden for lv in graded.levels for c in lv.cases)


def test_a_wrong_answer_is_a_failure_with_a_readable_message(toy):
    graded = runner.grade(toy, BROKEN_TOTAL, [2])
    failed = [c for lv in graded.levels for c in lv.cases if not c.passed]
    assert failed, "the broken total() should fail level 2"
    assert failed[0].status == "failed"
    assert "expected 7" in failed[0].message


def test_earlier_levels_are_re_run_and_can_regress(toy):
    graded = runner.grade(toy, BROKEN_TOTAL, [1, 2, 3, 4])
    assert graded.level(1).all_passed
    assert not graded.level(2).all_passed
    assert not graded.all_passed


def test_a_missing_class_reports_one_clear_error_per_case(toy):
    graded = runner.grade(toy, "class Nope:\n    pass\n", [1])
    assert "must define a class named `Counter`" in graded.load_error
    assert all(c.status == "error" for lv in graded.levels for c in lv.cases)


def test_a_syntax_error_is_reported_not_crashed(toy):
    graded = runner.grade(toy, "class Counter:\n    def add(self)\n", [1])
    assert graded.load_error
    assert "SyntaxError" in graded.load_error


def test_an_unexpected_exception_is_an_error_not_a_failure(toy):
    code = toy.canonical_code.replace(
        "        return sum(self._values)", "        raise ValueError('boom')")
    graded = runner.grade(toy, code, [2])
    case = graded.level(2).cases[0]
    assert case.status == "error"
    assert "ValueError" in case.message


def test_an_infinite_loop_times_out_that_case_only(toy):
    code = toy.canonical_code.replace(
        "        return sum(self._values)",
        "        while True:\n            pass")
    graded = runner.grade(toy, code, [1, 2])
    assert graded.level(1).all_passed, "level 1 does not call total()"
    assert graded.level(2).cases[0].status == "timeout"


def test_printing_is_captured_and_a_print_bomb_is_truncated(toy):
    chatty = toy.canonical_code.replace(
        "        return sum(self._values)",
        "        print('hello from total')\n        return sum(self._values)")
    graded = runner.grade(toy, chatty, [2])
    assert "hello from total" in graded.level(2).cases[0].stdout

    bomb = toy.canonical_code.replace(
        "        return sum(self._values)",
        "        for _ in range(200000):\n"
        "            print('x' * 200)\n"
        "        return sum(self._values)")
    graded = runner.grade(toy, bomb, [2])
    case = graded.level(2).cases[0]
    assert len(case.stdout) <= 4000, "stored output must stay bounded"
    assert "truncated" in case.stdout


def test_module_level_output_is_attached_to_the_first_case(toy):
    graded = runner.grade(toy, "print('at import')\n" + toy.canonical_code, [1])
    assert "at import" in graded.level(1).cases[0].stdout


def test_the_solution_cannot_import_the_application_from_the_sandbox(toy):
    """sys.path[0] is the run directory, not the package the harness lives in."""
    probe = toy.canonical_code.replace(
        "        return sum(self._values)",
        "        import importlib.util\n"
        "        for name in ('icf', 'app', 'config', 'runner', 'store'):\n"
        "            if importlib.util.find_spec(name) is not None:\n"
        "                raise AssertionError('reachable: ' + name)\n"
        "        return sum(self._values)")
    graded = runner.grade(toy, probe, [2])
    case = graded.level(2).cases[0]
    assert case.passed, case.message


def _docker_ready() -> bool:
    if shutil.which("docker") is None:
        return False
    probe = subprocess.run(
        ["docker", "image", "inspect", core_settings.DOCKER_IMAGE],
        capture_output=True, check=False)
    return probe.returncode == 0


@pytest.mark.skipif(not _docker_ready(),
                    reason="needs docker and the lootcode-runner image")
def test_grading_works_on_the_docker_backend_too(toy, monkeypatch):
    """ICF must honour EXECUTOR_BACKEND — an operator who chose containment
    for /problems must not silently lose it here.

    This is also the only test that exercises the whole ICF harness *as a
    different user*: the container runs as `nobody` and the server reads the
    results back, which has broken twice (the run directory's mode, then the
    result file's).
    """
    monkeypatch.setattr(core_settings, "EXECUTOR_BACKEND", "docker")
    graded = runner.grade(toy, toy.canonical_code, [1, 2, 3, 4])
    assert graded.all_passed, graded
    assert graded.passed_count == 8
