def countOfAtoms(formula):
    from collections import Counter
    n = len(formula)
    stack = [Counter()]
    i = 0
    while i < n:
        c = formula[i]
        if c == '(':
            stack.append(Counter()); i += 1
        elif c == ')':
            i += 1
            start = i
            while i < n and formula[i].isdigit():
                i += 1
            mult = int(formula[start:i] or 1)
            top = stack.pop()
            for el, cnt in top.items():
                stack[-1][el] += cnt * mult
        else:
            start = i; i += 1
            while i < n and formula[i].islower():
                i += 1
            name = formula[start:i]
            start = i
            while i < n and formula[i].isdigit():
                i += 1
            cnt = int(formula[start:i] or 1)
            stack[-1][name] += cnt
    counter = stack[0]
    return "".join(name + (str(counter[name]) if counter[name] > 1 else "")
                   for name in sorted(counter))
