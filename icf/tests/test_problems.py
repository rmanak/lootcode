"""The shipped problem bank. Guards against a problem being edited into a
state where it would be served but could not be solved."""
from __future__ import annotations

import pytest

from icf import content
from icf.config import settings
from icf.scripts.verify_icf import verify

SHIPPED = content.load_all(settings.PROBLEMS_DIR)
SLUGS = [p.slug for p in SHIPPED]


def test_there_is_at_least_one_problem():
    assert SLUGS, "icf/problems/ is empty — the feature has nothing to serve"


@pytest.mark.parametrize("slug", SLUGS)
def test_every_shipped_problem_validates(slug):
    problem = content.load(slug, settings.PROBLEMS_DIR)
    assert content.validate(problem) == []


@pytest.mark.parametrize("slug", SLUGS)
def test_every_shipped_problem_declares_four_populated_levels(slug):
    problem = content.load(slug, settings.PROBLEMS_DIR)
    assert [lv.number for lv in problem.levels] == [1, 2, 3, 4]
    for level in problem.levels:
        assert level.visible_cases, f"level {level.number} has no visible cases"
        assert level.hidden_cases, f"level {level.number} has no hidden cases"
        assert level.statement_md.strip()


@pytest.mark.slow
@pytest.mark.parametrize("slug", SLUGS)
def test_every_shipped_canonical_passes_and_every_level_earns_its_place(slug):
    """The same gate as ``icf/scripts/verify_icf.py``, in the suite.

    Slow — it runs the whole bank through the sandbox — but it is the only
    check that a level's tests actually fail before that level is written.
    """
    problem = content.load(slug, settings.PROBLEMS_DIR)
    assert verify(problem) == []
