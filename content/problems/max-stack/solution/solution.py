def maxStack(operations):
    stack = []
    out = []
    for op in operations:
        if op[0] == "push":
            stack.append(op[1])
            out.append(None)
        elif op[0] == "pop":
            out.append(stack.pop())
        elif op[0] == "top":
            out.append(stack[-1])
        elif op[0] == "peekMax":
            out.append(max(stack))
        else:
            m = max(stack)
            for i in range(len(stack) - 1, -1, -1):
                if stack[i] == m:
                    stack.pop(i)
                    break
            out.append(m)
    return out
