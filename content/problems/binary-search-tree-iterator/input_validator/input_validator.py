"""Input-constraint validator for problem 'binary-search-tree-iterator'.

`validate_input(...)` returns True iff its arguments satisfy the input
constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Hand-tightened: the generated check is kept as `_generated_validate_input`;
`validate_input` (bottom of file) adds the statement's input promises it
skipped. Do not overwrite this file with regenerated output; that drops them.
"""

def _generated_validate_input(operations):
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


# --- Hand-added: statement promises the generated check skipped --------------
# The statement promises these about the input; they are checkable from the
# input alone, so they belong here (see docs/input-validators.md):
#   - The first operation's tree is a binary search tree.
#   - `next()` calls are always valid (never more than the number of nodes).

class _Node:
    def __init__(self, val):
        self.val, self.left, self.right = val, None, None


def _tree(root):
    """A node object for ``root`` (level-order list or already a node)."""
    if not isinstance(root, list):
        return root
    if not root or root[0] is None:
        return None
    nodes = [_Node(root[0])]
    queue, i = [nodes[0]], 1
    while queue and i < len(root):
        cur = queue.pop(0)
        for side in ("left", "right"):
            if i < len(root) and root[i] is not None:
                child = _Node(root[i])
                setattr(cur, side, child)
                queue.append(child)
            i += 1
    return nodes[0]


def _inorder(root):
    out, stack, node = [], [], _tree(root)
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        out.append(node.val)
        node = node.right
    return out



def _stated_promises(operations):
    vals = _inorder(operations[0][1])
    if any(a >= b for a, b in zip(vals, vals[1:])):
        return False
    return sum(op[0] == "next" for op in operations[1:]) <= len(vals)


def validate_input(operations):
    if not _generated_validate_input(operations):
        return False
    try:
        return bool(_stated_promises(operations))
    except Exception:  # malformed input the generated check let through
        return False
