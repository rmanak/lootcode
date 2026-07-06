"""Input-constraint validator for problem 'average-of-levels-in-binary-tree'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(root):
    if not isinstance(root, list):
        return False
    if len(root) < 1:
        return False
    node_count = 0
    for x in root:
        if x is None:
            continue
        if isinstance(x, bool) or not isinstance(x, int):
            return False
        if x < -2147483648 or x > 2147483647:
            return False
        node_count += 1
    if node_count < 1 or node_count > 10000:
        return False
    return True
