def solveEquation(equation):
    def parse(expr):
        coef = const = 0
        i, n = 0, len(expr)
        while i < n:
            sign = 1
            if expr[i] == '+':
                i += 1
            elif expr[i] == '-':
                sign = -1; i += 1
            j = i
            while j < n and expr[j].isdigit():
                j += 1
            num = expr[i:j]
            if j < n and expr[j] == 'x':
                coef += sign * (int(num) if num else 1)
                i = j + 1
            else:
                const += sign * (int(num) if num else 0)
                i = j
        return coef, const
    lhs, rhs = equation.split('=')
    lc, lk = parse(lhs)
    rc, rk = parse(rhs)
    a = lc - rc
    b = rk - lk
    if a == 0:
        return "Infinite solutions" if b == 0 else "No solution"
    return "x=" + str(b // a)
