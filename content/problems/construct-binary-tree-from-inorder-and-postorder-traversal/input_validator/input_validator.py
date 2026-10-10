"""Input-constraint validator for problem 'construct-binary-tree-from-inorder-and-postorder-traversal'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(inorder, postorder):
    if not isinstance(inorder, list) or not isinstance(postorder, list):
        return False
    if len(inorder) < 1 or len(inorder) > 3000:
        return False
    if len(postorder) != len(inorder):
        return False
    for x in inorder:
        if isinstance(x, bool) or not isinstance(x, int) or x < -3000 or x > 3000:
            return False
    for x in postorder:
        if isinstance(x, bool) or not isinstance(x, int) or x < -3000 or x > 3000:
            return False
    if len(set(inorder)) != len(inorder):
        return False
    if len(set(postorder)) != len(postorder):
        return False
    inorder_set = set(inorder)
    for x in postorder:
        if x not in inorder_set:
            return False
    return True


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - `inorder` and `postorder` consist of unique values and are the inorder
#     and postorder traversals of the same binary tree.

def _stated_promises(inorder, postorder):
    if len(set(postorder)) != len(postorder) or set(postorder) != set(inorder):
        return False
    pos = {v: i for i, v in enumerate(inorder)}
    stack = [(0, 0, len(postorder))]          # (postorder start, inorder start, size)
    while stack:
        p, i, size = stack.pop()
        if size == 0:
            continue
        k = pos[postorder[p + size - 1]]
        if not i <= k < i + size:
            return False
        left = k - i
        stack.append((p, i, left))
        stack.append((p + left, k + 1, size - 1 - left))
    return True


def validate_input(inorder, postorder):
    if not _generated_validate_input(inorder, postorder):
        return False
    try:
        return bool(_stated_promises(inorder, postorder))
    except Exception:  # malformed input the generated check let through
        return False
