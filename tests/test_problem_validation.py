"""The pre-save gate (app/problem_validation.py).

Every admin write — the manual New-problem form, the edit form, and the AI
review-before-save step — goes through ``validate_problem``. It is 479 lines and
had no test at all, which means nothing caught a regression in the one thing
standing between a broken problem and the bank.

The behavioral tier (running the canonical in the real sandbox) is the slow,
authoritative step; it is exercised in its own ``slow``-marked tests and switched
off with ``run_behavioral=False`` everywhere else so the structural rules stay
fast to test.
"""
import pytest

from app.problem_validation import (
    ValidationResult,
    existing_slugs,
    find_similar_problems,
    suggest_slug,
    validate_problem,
)

CANONICAL = (
    "def addTwo(a, b):\n"
    "    return a + b\n"
)


def good(**over) -> dict:
    """A minimally valid problem dict, in the shape `_form_to_data` produces."""
    data = {
        "slug": "add-two", "title": "Add Two", "difficulty": "easy",
        "topics": ["math"], "hints": [], "statement_md": "Return `a + b`.",
        "kind": "function", "function_name": "addTwo",
        "params": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
        "return_type": "int", "compare": "exact",
        "starter_code": "def addTwo(a, b):\n    pass\n",
        "canonical_solution": CANONICAL,
        "scoring_type": "weighted", "points": 100, "source": "test",
        "class_name": None, "class_methods": None,
        # The structural gate requires at least 4 cases.
        "tests": [
            {"name": "c1", "input": {"a": 1, "b": 2}, "expected": 3,
             "weight": 1, "hidden": False},
            {"name": "c2", "input": {"a": -5, "b": 5}, "expected": 0,
             "weight": 1, "hidden": True},
            {"name": "c3", "input": {"a": 0, "b": 0}, "expected": 0,
             "weight": 1, "hidden": True},
            {"name": "c4", "input": {"a": -7, "b": -8}, "expected": -15,
             "weight": 1, "hidden": True},
        ],
    }
    data.update(over)
    return data


def list_returning(**over) -> dict:
    """A problem whose answer is a list — needed for the non-`exact` compare modes."""
    data = good(
        slug="evens", title="Evens", function_name="evens",
        params=[{"name": "nums", "type": "int[]"}], return_type="int[]",
        canonical_solution="def evens(nums):\n    return [n for n in nums if n % 2 == 0]\n",
        starter_code="def evens(nums):\n    pass\n",
        tests=[
            {"name": "c1", "input": {"nums": [1, 2, 3, 4]}, "expected": [2, 4],
             "weight": 1, "hidden": False},
            {"name": "c2", "input": {"nums": []}, "expected": [],
             "weight": 1, "hidden": True},
            {"name": "c3", "input": {"nums": [1, 3]}, "expected": [],
             "weight": 1, "hidden": True},
            {"name": "c4", "input": {"nums": [-2, 0, 7]}, "expected": [-2, 0],
             "weight": 1, "hidden": True},
        ])
    data.update(over)
    return data


def check(**over) -> ValidationResult:
    """Validate without paying for the sandbox."""
    return validate_problem(good(**over), db=None, is_new=False,
                            run_behavioral=False)


def errors_mentioning(res: ValidationResult, needle: str) -> list[str]:
    return [e for e in res.errors if needle.lower() in e.lower()]


# --- the happy path -------------------------------------------------------
def test_a_sound_problem_passes():
    res = check()
    assert res.ok, res.errors
    assert res.errors == []


def test_ok_is_driven_by_errors_not_warnings():
    res = check(topics=["bfs"])           # an alias — warns, never blocks
    assert res.ok
    assert any("fold" in w for w in res.warnings)


# --- slug -----------------------------------------------------------------
@pytest.mark.parametrize("slug", [
    "Add-Two",        # uppercase
    "add_two",        # underscore
    "add--two",       # doubled hyphen
    "-add-two",       # leading hyphen
    "add-two-",       # trailing hyphen
    "add two",        # space
    "add/two",        # path separator — would escape the content dir
])
def test_bad_slugs_are_refused(slug):
    assert errors_mentioning(check(slug=slug), "kebab-case")


def test_missing_slug_and_title_are_refused():
    res = check(slug="", title="")
    assert errors_mentioning(res, "slug is required")
    assert errors_mentioning(res, "title is required")


def test_slug_collision_is_only_checked_for_new_problems(client, db):
    # `client` seeds the bank into the temp DB; two-sum is certainly in it.
    data = good(slug="two-sum")
    editing = validate_problem(data, db=db, is_new=False, run_behavioral=False)
    assert not errors_mentioning(editing, "already exists")

    creating = validate_problem(data, db=db, is_new=True, run_behavioral=False)
    assert errors_mentioning(creating, "already exists")
    # ...and it must suggest a free alternative rather than just saying no.
    assert "two-sum-2" in " ".join(creating.errors)


# --- tags -----------------------------------------------------------------
def test_invented_tags_are_a_hard_error():
    res = check(topics=["array", "quantum-annealing"])
    assert errors_mentioning(res, "quantum-annealing")
    assert not res.ok


def test_known_aliases_are_accepted_with_a_warning():
    res = check(topics=["bfs"])
    assert res.ok
    assert any("'bfs' → 'breadth-first-search'" in w for w in res.warnings)


def test_dropped_tags_warn_rather_than_block():
    res = check(topics=["array", "enumeration"])
    assert res.ok
    assert any("too vague" in w for w in res.warnings)


# --- statement <-> compare consistency -----------------------------------
def test_any_order_statement_with_exact_compare_is_refused():
    res = check(statement_md="Return the pairs in any order.", compare="exact")
    assert errors_mentioning(res, "any order")


def test_any_order_is_fine_once_compare_is_relaxed():
    # compare='unordered' also demands list-shaped expecteds, so this swaps in a
    # list-returning problem rather than just flipping the mode.
    res = validate_problem(list_returning(
        statement_md="Return the values in any order.", compare="unordered"),
        db=None, is_new=False, run_behavioral=False)
    assert res.ok, res.errors


def test_ambiguity_check_survives_line_wrapping():
    # The phrase is detected after whitespace collapsing, so a hard-wrapped
    # statement can't smuggle it past.
    res = check(statement_md="Return the pairs in any\norder.", compare="exact")
    assert errors_mentioning(res, "any order")


# --- structural (delegated to scripts/test_llm_output.py) -----------------
def test_canonical_must_define_the_declared_function():
    res = check(canonical_solution="def somethingElse(a, b):\n    return a + b\n")
    assert not res.ok


def test_test_input_keys_must_match_the_parameter_names():
    res = check(tests=[{"name": "c1", "input": {"a": 1, "wrong": 2},
                        "expected": 3, "weight": 1, "hidden": False}])
    assert not res.ok


def test_an_empty_test_suite_is_refused():
    assert not check(tests=[]).ok


def test_unparseable_canonical_is_refused():
    res = check(canonical_solution="def addTwo(a, b:\n    return a + b\n")
    assert not res.ok


def test_a_misspelled_rich_type_is_surfaced():
    # "TreeNod" would be treated as a plain value and silently break decoding.
    res = check(params=[{"name": "a", "type": "TreeNod"},
                        {"name": "b", "type": "int"}])
    assert res.warnings, "a bogus type label should at least warn"


# --- slug helpers ---------------------------------------------------------
def test_suggest_slug_finds_the_first_free_suffix():
    assert suggest_slug("x", set()) == "x"
    assert suggest_slug("x", {"x"}) == "x-2"
    assert suggest_slug("x", {"x", "x-2", "x-3"}) == "x-4"


def test_suggest_slug_gives_up_gracefully():
    taken = {"x"} | {f"x-{n}" for n in range(2, 100)}
    assert suggest_slug("x", taken) == "x"


def test_existing_slugs_unions_db_and_disk(db):
    slugs = existing_slugs(db)
    assert "two-sum" in slugs
    # Disk is included even without a DB, so an unseeded on-disk problem still
    # blocks a colliding new slug.
    assert "two-sum" in existing_slugs(None)


# --- duplicate nudge ------------------------------------------------------
def test_find_similar_problems_is_never_a_gate(db):
    hits = find_similar_problems(db, slug="two-sum-again", title="Two Sum Again",
                                 tags=["array", "hash-table"])
    assert hits, "an obvious near-duplicate should surface"
    assert all({"slug", "title", "difficulty", "shared_tags", "matched"} <= set(h)
               for h in hits)
    # It never returns the problem being edited.
    assert all(h["slug"] != "two-sum-again" for h in hits)


def test_find_similar_problems_requires_a_name_overlap(db):
    # Sharing only tags is not similarity — otherwise every "array" problem
    # would flood the list.
    hits = find_similar_problems(
        db, slug="zzqqxx-unrelated", title="Zzqqxx Unrelated", tags=["array"])
    assert hits == []


def test_find_similar_problems_without_a_db_is_empty():
    assert find_similar_problems(None, slug="x", title="X", tags=[]) == []


def test_find_similar_problems_respects_the_limit(db):
    assert len(find_similar_problems(db, slug="sum-of-two-numbers",
                                     title="Sum of Two Numbers", tags=None,
                                     limit=3)) <= 3


# --- the behavioral tier (real sandbox) ----------------------------------
@pytest.mark.slow
def test_behavioral_tier_accepts_a_correct_canonical():
    res = validate_problem(good(), db=None, is_new=False, run_behavioral=True)
    assert res.ok, res.errors
    assert res.solved is True
    assert res.behavioral == "4/4 tests passed"


@pytest.mark.slow
def test_behavioral_tier_rejects_a_canonical_that_fails_its_own_tests():
    data = good(canonical_solution="def addTwo(a, b):\n    return a - b\n")
    res = validate_problem(data, db=None, is_new=False, run_behavioral=True)
    assert not res.ok
    assert res.solved is False
    assert errors_mentioning(res, "does not pass all of its own tests")


@pytest.mark.slow
def test_behavioral_tier_is_skipped_when_the_structure_is_already_broken():
    # The sandbox is the expensive step; a structurally broken problem must
    # never reach it.
    res = validate_problem(good(slug="Bad Slug"), db=None, is_new=True,
                           run_behavioral=True)
    assert not res.ok
    assert res.solved is None and res.behavioral == ""
