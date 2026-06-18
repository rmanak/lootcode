def calculate(s):
    stack = []
    num = 0
    op = '+'
    for ch in s + '+':
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch in '+-*/':
            if op == '+':
                stack.append(num)
            elif op == '-':
                stack.append(-num)
            elif op == '*':
                stack.append(stack.pop() * num)
            else:
                prev = stack.pop()
                q = abs(prev) // num
                stack.append(-q if prev < 0 else q)
            op = ch
            num = 0
    return sum(stack)
