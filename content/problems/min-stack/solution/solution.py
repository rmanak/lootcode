def minStackOps(operations):
    stack, mins, out = [], [], []
    for op in operations:
        name = op[0]
        if name == "push":
            x = op[1]
            stack.append(x)
            mins.append(x if not mins else min(x, mins[-1]))
            out.append(None)
        elif name == "pop":
            stack.pop()
            mins.pop()
            out.append(None)
        elif name == "top":
            out.append(stack[-1])
        else:
            out.append(mins[-1])
    return out
