def clumsy(N):
    stack = [N]
    num = N - 1
    op = 0
    while num > 0:
        if op == 0:
            stack.append(stack.pop() * num)
        elif op == 1:
            top = stack.pop()
            stack.append(int(top / num))
        elif op == 2:
            stack.append(num)
        else:
            stack.append(-num)
        op = (op + 1) % 4
        num -= 1
    return sum(stack)
