def nextLargerNodes(head):
    res = [0] * len(head)
    stack = []
    for i, v in enumerate(head):
        while stack and head[stack[-1]] < v:
            res[stack.pop()] = v
        stack.append(i)
    return res
