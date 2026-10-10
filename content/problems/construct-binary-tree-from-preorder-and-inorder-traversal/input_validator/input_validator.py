"""Input-constraint validator for problem 'construct-binary-tree-from-preorder-and-inorder-traversal'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(preorder, inorder):
    if not isinstance(preorder, list) or not isinstance(inorder, list):
        return False
    if len(preorder) < 1 or len(preorder) > 3000:
        return False
    if len(inorder) != len(preorder):
        return False
    for x in preorder:
        if isinstance(x, bool) or not isinstance(x, int) or x < -3000 or x > 3000:
            return False
    for x in inorder:
        if isinstance(x, bool) or not isinstance(x, int) or x < -3000 or x > 3000:
            return False
    if len(set(preorder)) != len(preorder):
        return False
    if set(preorder) != set(inorder):
        return False
    return True


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - All values are unique.
#   - `inorder` is a permutation of `preorder` consistent with some binary
#     tree.

def _stated_promises(preorder, inorder):
    if len(set(preorder)) != len(preorder) or set(preorder) != set(inorder):
        return False
    pos = {v: i for i, v in enumerate(inorder)}
    stack = [(0, 0, len(preorder))]           # (preorder start, inorder start, size)
    while stack:
        p, i, size = stack.pop()
        if size == 0:
            continue
        k = pos[preorder[p]]
        if not i <= k < i + size:
            return False
        left = k - i
        stack.append((p + 1, i, left))
        stack.append((p + 1 + left, k + 1, size - 1 - left))
    return True


def validate_input(preorder, inorder):
    if not _generated_validate_input(preorder, inorder):
        return False
    try:
        return bool(_stated_promises(preorder, inorder))
    except Exception:  # malformed input the generated check let through
        return False
