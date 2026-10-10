"""Input-constraint validator for problem 'construct-binary-search-tree-from-preorder-traversal'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(preorder):
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


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - `preorder` is the preorder traversal of a binary search tree (values
#     distinct).

def _stated_promises(preorder):
    if len(set(preorder)) != len(preorder):
        return False
    low, stack = None, []
    for v in preorder:
        if low is not None and v < low:
            return False
        while stack and stack[-1] < v:
            low = stack.pop()
        stack.append(v)
    return True


def validate_input(preorder):
    if not _generated_validate_input(preorder):
        return False
    try:
        return bool(_stated_promises(preorder))
    except Exception:  # malformed input the generated check let through
        return False
