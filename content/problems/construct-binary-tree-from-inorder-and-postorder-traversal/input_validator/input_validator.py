"""Input-constraint validator for problem 'construct-binary-tree-from-inorder-and-postorder-traversal'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(inorder, postorder):
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
