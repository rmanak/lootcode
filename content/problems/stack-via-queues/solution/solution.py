def myStack(operations):
    from collections import deque
    q = deque()
    out = []
    for op in operations:
        if op[0] == "push":
            q.append(op[1])
            for _ in range(len(q) - 1):
                q.append(q.popleft())
            out.append(None)
        elif op[0] == "pop":
            out.append(q.popleft())
        elif op[0] == "top":
            out.append(q[0])
        else:
            out.append(len(q) == 0)
    return out
