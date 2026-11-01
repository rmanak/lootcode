"""The judge's comparison modes, in the trusted parent (``app/executor._equal``).

No sandbox here: ``_equal`` sees two values that have both been through JSON,
so these are plain-data unit tests. The end-to-end runs that put a real
submission through each mode live in ``test_executor.py``.
"""
import math

import pytest

from app.executor import CLOSE_ABS_TOL, CLOSE_REL_TOL, _equal


@pytest.mark.parametrize("got,expected", [
    (0.1 + 0.2, 0.3),                                  # last-bit noise
    (1.0 + 5e-7, 1.0),                                 # inside the relative tolerance
    (1e-12, 0.0),                                      # inside the absolute tolerance
    (-0.0, 0.0),
    (3, 3.0),                                          # an int answer to a float expected
    (math.inf, math.inf),
    ([0.30000000000000004, [1e-17, 2.0]], [0.3, [0.0, 2.0]]),  # (loss, grad)
    ({"loss": 0.1 + 0.2, "dW": [[1.0]]}, {"loss": 0.3, "dW": [[1.0]]}),
    ([True, "a", None], [True, "a", None]),
])
def test_close_accepts_float_noise(got, expected):
    assert _equal(got, expected, "close")


@pytest.mark.parametrize("got,expected", [
    (1.0 + 1e-5, 1.0),                                 # a real difference
    (1e-8, 0.0),                                       # outside the absolute tolerance
    (math.nan, math.nan),                              # NaN never matches
    (math.inf, -math.inf),
    ([1.0, 2.0], [2.0, 1.0]),                          # order still matters
    ([1.0, 2.0], [1.0, 2.0, 3.0]),                     # so does length
    ([1.0], 1.0),                                      # and shape
    ({"loss": 1.0}, {"loss": 1.0, "grad": []}),        # and keys
    ("0.3", 0.3),
    (None, 0.0),
])
def test_close_rejects_real_differences(got, expected):
    assert not _equal(got, expected, "close")


def test_close_compares_two_ints_exactly():
    # A label, an argmax index or a count is right or wrong; 1e-6 relative
    # would let 2000001 pass for 2000000.
    assert _equal(2000000, 2000000, "close")
    assert not _equal(2000001, 2000000, "close")
    assert _equal(2000000.0000001, 2000000, "close")  # a float side still gets tolerance


@pytest.mark.parametrize("got,expected", [
    (10**400, 0.5),
    ([10**400], [1.0]),
    (0.5, 10**400),
])
def test_close_survives_ints_past_float_range(got, expected):
    # The returned value is the sandbox's to choose; math.isclose raises
    # OverflowError on it, which used to escape the grader as a 500.
    assert not _equal(got, expected, "close")


def test_close_does_not_treat_bools_as_numbers():
    # Exactly what `exact` does with them: no tolerance, Python equality.
    assert _equal(True, True, "close")
    assert not _equal(True, False, "close")
    assert not _equal(False, 1e-12, "close")


def test_exact_is_still_exact_about_floats():
    # The reason `close` exists: correct float code rarely matches bit for bit.
    assert not _equal(0.1 + 0.2, 0.3, "exact")


def test_the_tolerances_are_the_documented_ones():
    # Quoted in specs/problem-schema.md, the authoring guidelines and the
    # generation prompt. Changing them changes what every statement promises.
    assert (CLOSE_REL_TOL, CLOSE_ABS_TOL) == (1e-6, 1e-9)
