def scoreOfParentheses(S):
    stack = [0]
    for c in S:
        if c == '(':
            stack.append(0)
        else:
            v = stack.pop()
            stack[-1] += max(2 * v, 1)
    return stack[0]
