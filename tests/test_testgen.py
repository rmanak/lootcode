"""Tests for the test-strengthening toolkit (app/testgen + strengthen_tests).

These lock in the fairness/robustness fixes so they can't silently regress:
  - length-domain filter (no out-of-domain []/short arrays),
  - op-name-safe seed perturbation (no findMedian->fbndMedian corruption),
  - seed-invariant guard (sorted / permutation / rotated preconditions),
  - candidate extraction + the unsafe-code screen for the LLM population.
"""
from app.testgen.constraints import parse_constraints, size_bounds
from app.testgen.generators import (
    GenConfig,
    array_satisfies,
    generate_candidates,
    intmatrix_satisfies,
    learn_array_invariants,
    learn_intmatrix_domain,
)
from app.testgen import candidates as C


# --------------------------------------------------------------------------- #
# Seed-invariant learning
# --------------------------------------------------------------------------- #
def test_learn_invariants_sorted_distinct():
    seeds = [[1, 2, 3], [0, 5, 9, 20], [2, 4, 6, 8], [1, 7], [3, 4, 5, 6]]
    inv = learn_array_invariants(seeds)
    assert "asc" in inv
    assert "rot" in inv          # sorted-distinct arrays are trivially "rotated"
    assert "desc" not in inv


def test_learn_invariants_permutation():
    seeds = [[0, 1, 2], [2, 0, 1, 3], [1, 0], [3, 1, 2, 0]]
    inv = learn_array_invariants(seeds)
    assert "perm0" in inv


def test_learn_invariants_rotated_only():
    # rotations of a sorted-distinct array: exactly one cyclic descent, not sorted
    seeds = [[4, 5, 1, 2, 3], [3, 4, 5, 1, 2], [2, 3, 1], [5, 1, 2, 3, 4]]
    inv = learn_array_invariants(seeds)
    assert "rot" in inv
    assert "asc" not in inv


def test_learn_invariants_none_for_arbitrary():
    seeds = [[3, 1, 2], [5, 5, 1, 9], [2, 8, 1, 1, 4], [9, 0, 3]]
    assert learn_array_invariants(seeds) == set()


def test_learn_invariants_needs_enough_seeds():
    # too few examples -> refuse to infer (avoids a spurious invariant)
    assert learn_array_invariants([[1, 2, 3]]) == set()
    assert learn_array_invariants([[1, 2], [3, 4]]) == set()


def test_array_satisfies():
    assert array_satisfies([1, 2, 3], {"asc"})
    assert not array_satisfies([3, 2, 1], {"asc"})
    assert not array_satisfies([1, 2, 2], {"rot"})       # dup breaks distinctness
    assert array_satisfies([3, 4, 1, 2], {"rot"})        # a valid rotation
    assert not array_satisfies([2, 3, 1, 0, 4, 4], {"rot"})
    assert array_satisfies([0, 1, 2], {"perm0"})
    assert not array_satisfies([0, 1, 3], {"perm0"})
    assert array_satisfies([], {"asc", "perm0"})          # empty deferred to other filters


# --------------------------------------------------------------------------- #
# Graph node-label domain (A+ fairness guard for int[][] edge/adjacency params)
# --------------------------------------------------------------------------- #
def test_intmatrix_domain_scalar_bound():
    # course-schedule shape: prerequisites labels bounded by numCourses
    mats = [[[1, 0], [0, 2]], [[0, 1]], [[2, 1], [1, 0], [0, 2]]]
    scal = {"numCourses": [3, 2, 3]}
    dom = learn_intmatrix_domain("prerequisites", mats, scal)
    assert dom.get("nonneg") and dom.get("lt_params") == ["numCourses"]
    # the actual unfair cases from the dry-run must now be rejected
    assert not intmatrix_satisfies([[-34, -35]], dom, {"numCourses": 118})   # negative
    assert not intmatrix_satisfies([[1, 3]], dom, {"numCourses": 3})         # node >= n
    assert not intmatrix_satisfies([[2, 2]], dom, {"numCourses": 0})         # n=0, any ref invalid
    assert intmatrix_satisfies([[1, 0], [2, 1]], dom, {"numCourses": 3})     # valid


def test_intmatrix_domain_adjacency_self_bound():
    # all-paths shape: graph[i] lists neighbours, each a valid row index
    mats = [[[1, 2], [3], [3], []], [[1], [2], []], [[1, 2, 3], [2], [3], []]]
    dom = learn_intmatrix_domain("graph", mats, {})
    assert dom.get("lt_len") and dom.get("nonneg")
    assert not intmatrix_satisfies([[3], [], [5, 5], [5]], dom, {})   # node 5 in 4-node graph
    assert intmatrix_satisfies([[1], [2], [3], []], dom, {})          # valid DAG


def test_intmatrix_domain_weighted_edges_endpoints_only():
    # weighted edges [u, v, w]: w may exceed n; only endpoints are node labels
    mats = [[[0, 1, 50], [1, 2, 99]], [[0, 2, 40]], [[2, 0, 7], [1, 2, 88]]]
    scal = {"n": [3, 3, 3]}
    dom = learn_intmatrix_domain("edges", mats, scal)
    assert dom.get("lt_params") == ["n"]              # learned despite big weights
    assert intmatrix_satisfies([[0, 1, 100]], dom, {"n": 3})    # big weight is fine
    assert not intmatrix_satisfies([[0, 5, 10]], dom, {"n": 3})  # endpoint 5 >= n


def test_intmatrix_domain_ignores_value_grids():
    # a matrix/grid of values (even all-nonnegative) must NOT be treated as a graph
    grid = [[[1, 0, 1], [0, 1, 0]], [[1, 1], [0, 0]], [[0, 1, 1], [1, 0, 1]]]
    assert learn_intmatrix_domain("grid", grid, {}) is None
    assert learn_intmatrix_domain("matrix", grid, {}) is None
    # coordinate pairs (can legitimately be anything) aren't graphs either
    pts = [[[1, 2], [3, 4]], [[0, 5]], [[2, 2], [9, 1]]]
    assert learn_intmatrix_domain("points", pts, {}) is None


def test_intmatrix_domain_needs_enough_seeds():
    assert learn_intmatrix_domain("edges", [[[0, 1]]], {"n": [2]}) is None


# --------------------------------------------------------------------------- #
# Length-domain filter (parsed size bounds)
# --------------------------------------------------------------------------- #
def test_size_bounds_parsed():
    b = parse_constraints("Constraints:\n- `2 <= nums.length <= 10^4`\n")
    assert size_bounds(b, "nums") == (2, 10000)


def test_generate_respects_min_length():
    params = [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}]
    seeds = [{"nums": [2, 7, 11, 15], "target": 9}]
    bounds = parse_constraints("`2 <= nums.length <= 100`\n`-100 <= nums[i] <= 100`")
    cands = generate_candidates(params, seeds, bounds, GenConfig(n_fuzz=200, seed=1))
    assert cands, "should produce candidates"
    for c in cands:
        assert len(c.input["nums"]) >= 2, f"out-of-domain length: {c.input['nums']}"


def test_generate_respects_learned_invariant():
    # all seeds sorted-distinct -> generated arrays must stay sorted
    params = [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}]
    seeds = [{"nums": s, "target": 3} for s in
             ([1, 2, 3, 4], [0, 5, 9], [2, 4, 6, 8], [1, 3, 7, 9], [0, 1, 2])]
    cands = generate_candidates(params, seeds, {}, GenConfig(n_fuzz=300, seed=2))
    for c in cands:
        nums = c.input["nums"]
        assert nums == sorted(nums), f"non-sorted generated for sorted problem: {nums}"


# --------------------------------------------------------------------------- #
# Op-name-safe seed perturbation (design/streaming problems)
# --------------------------------------------------------------------------- #
def test_ops_param_names_not_corrupted():
    params = [{"name": "operations", "type": "any[][]"}]
    seeds = [{"operations": [["addNum", 3], ["addNum", 4], ["findMedian"],
                             ["addNum", 6], ["findMedian"]]}]
    cands = generate_candidates(params, seeds, {}, GenConfig(n_fuzz=300, seed=3))
    valid_ops = {"addNum", "findMedian"}
    for c in cands:
        for op in c.input["operations"]:
            assert op[0] in valid_ops, f"corrupted op name: {op[0]!r}"


# --------------------------------------------------------------------------- #
# LLM candidate extraction + safety screen
# --------------------------------------------------------------------------- #
def test_extract_code_from_fence():
    txt = "Here is my solution:\n```python\ndef f(x):\n    return x + 1\n```\nDone."
    assert C.extract_code(txt) == "def f(x):\n    return x + 1"


def test_extract_code_no_fence_falls_back():
    assert "def f" in C.extract_code("def f(x):\n    return x")


def test_validates_requires_function():
    assert C._validates("def two_sum(nums, target):\n    return []", "two_sum")
    assert not C._validates("def other(x):\n    return x", "two_sum")  # wrong name
    assert not C._validates("def two_sum(:\n  bad syntax", "two_sum")   # won't compile


def test_unsafe_screen():
    import scripts.strengthen_tests as st
    assert st._UNSAFE.search("import os\nos.system('rm -rf /')")
    assert st._UNSAFE.search("open('/etc/passwd').read()")
    assert st._UNSAFE.search("import subprocess")
    assert not st._UNSAFE.search("def f(a):\n    return sorted(a)[0]")


# --------------------------------------------------------------------------- #
# In-process TreeNode codec (fast-path grading for tree problems)
# --------------------------------------------------------------------------- #
def test_treenode_codec_roundtrip():
    from types import SimpleNamespace as NS
    import scripts.strengthen_tests as st
    # a solution that increments every node value — needs real TreeNode objects
    code = ("def bump(root):\n"
            "    if root is None:\n        return None\n"
            "    root.value += 1\n"
            "    bump(root.left)\n    bump(root.right)\n"
            "    return root\n")
    f = st._compile(code, "bump", {"TreeNode": st.TreeNode})
    prob = NS(params=[{"name": "root", "type": "TreeNode"}], return_type="TreeNode")
    decoders, encoder = st._tree_codec(prob)
    assert list(decoders) == ["root"] and encoder is not None
    # array in -> decoded to objects -> bumped -> encoded back to trimmed array
    assert st._call(f, {"root": [1, 2, 3, None, 4]}, decoders, encoder) == [2, 3, 4, None, 5]
    assert st._call(f, {"root": []}, decoders, encoder) == []


def test_treenode_fast_path_available():
    from types import SimpleNamespace as NS
    import scripts.strengthen_tests as st
    assert st._fast_available(NS(params=[{"name": "root", "type": "TreeNode"}],
                                 return_type="TreeNode"))
    # a *nested* TreeNode still needs the sandbox path
    assert not st._fast_available(NS(params=[{"name": "x", "type": "TreeNode[]"}],
                                     return_type="int"))
