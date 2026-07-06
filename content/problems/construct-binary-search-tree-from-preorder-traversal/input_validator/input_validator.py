"""Input-constraint validator for problem 'construct-binary-search-tree-from-preorder-traversal'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(preorder):
    if not isinstance(preorder, list):
        return False
    if len(preorder) < 1 or len(preorder) > 100:
        return False
    for x in preorder:
        if isinstance(x, bool) or not isinstance(x, int) or x < 1 or x > 100000000:
            return False
    if len(set(preorder)) != len(preorder):
        return False
    return True
