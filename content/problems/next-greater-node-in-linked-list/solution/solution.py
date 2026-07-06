def nextLargerNodes(head):
    vals = []
    node = head
    while node is not None:
        vals.append(node.val)
        node = node.next
    res = [0] * len(vals)
    stack = []
    for i, v in enumerate(vals):
        while stack and vals[stack[-1]] < v:
            res[stack.pop()] = v
        stack.append(i)
    return res
