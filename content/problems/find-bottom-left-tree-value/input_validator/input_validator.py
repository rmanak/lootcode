"""Input-constraint validator for problem 'find-bottom-left-tree-value'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(root):
    if root is None:
        return False
    count = 0
    stack = [root]
    while stack:
        node = stack.pop()
        count += 1
        if count > 10000:
            return False
        left = getattr(node, 'left', None)
        right = getattr(node, 'right', None)
        if left is not None:
            stack.append(left)
        if right is not None:
            stack.append(right)
    return True
