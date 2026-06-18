def evaluate(expression):
    def tokenize(s):
        res, bal, cur = [], 0, ''
        for ch in s:
            if ch == '(':
                bal += 1
            elif ch == ')':
                bal -= 1
            if ch == ' ' and bal == 0:
                res.append(cur)
                cur = ''
            else:
                cur += ch
        if cur:
            res.append(cur)
        return res

    def ev(expr, scope):
        if expr[0] != '(':
            if expr[0] == '-' or expr[0].isdigit():
                return int(expr)
            return scope[expr][-1]
        toks = tokenize(expr[1:-1])
        op = toks[0]
        if op == 'add':
            return ev(toks[1], scope) + ev(toks[2], scope)
        if op == 'mult':
            return ev(toks[1], scope) * ev(toks[2], scope)
        params = toks[1:]
        assigned = []
        for i in range(0, len(params) - 1, 2):
            scope.setdefault(params[i], []).append(ev(params[i + 1], scope))
            assigned.append(params[i])
        res = ev(params[-1], scope)
        for v in assigned:
            scope[v].pop()
        return res

    return ev(expression, {})
