"""Input-constraint validator for problem 'construct-binary-tree-from-preorder-and-inorder-traversal'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(preorder, inorder):
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
