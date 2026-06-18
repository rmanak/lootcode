def calculate(s):
    stack = []
    result = 0
    sign = 1
    num = 0
    for ch in s:
        if ch.isdigit():
            num = num * 10 + int(ch)
        elif ch == '+':
            result += sign * num
            num = 0
            sign = 1
        elif ch == '-':
            result += sign * num
            num = 0
            sign = -1
        elif ch == '(':
            stack.append(result)
            stack.append(sign)
            result = 0
            sign = 1
        elif ch == ')':
            result += sign * num
            num = 0
            result *= stack.pop()
            result += stack.pop()
    return result + sign * num
