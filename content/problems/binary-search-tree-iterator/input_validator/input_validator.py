"""Input-constraint validator for problem 'binary-search-tree-iterator'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.
"""

def validate_input(operations):
    if not isinstance(operations, list):
        return False
    if len(operations) < 1:
        return False
    if len(operations) - 1 > 100000:
        return False
    if not isinstance(operations[0], list):
        return False
    if len(operations[0]) != 2:
        return False
    if operations[0][0] != "BSTIterator":
        return False
    tree = operations[0][1]
    if not isinstance(tree, list):
        return False
    node_count = 0
    for val in tree:
        if val is None:
            continue
        if isinstance(val, bool) or not isinstance(val, int):
            return False
        if val < 0 or val > 1000000:
            return False
        node_count += 1
    if node_count < 1 or node_count > 100000:
        return False
    for i in range(1, len(operations)):
        if not isinstance(operations[i], list):
            return False
        if len(operations[i]) != 1:
            return False
        if operations[i][0] not in ("next", "hasNext"):
            return False
    return True
