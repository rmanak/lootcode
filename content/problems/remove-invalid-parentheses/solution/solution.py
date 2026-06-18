def removeInvalidParentheses(s):
    def valid(t):
        c = 0
        for ch in t:
            if ch == '(':
                c += 1
            elif ch == ')':
                c -= 1
                if c < 0:
                    return False
        return c == 0

    level = {s}
    while True:
        found = [t for t in level if valid(t)]
        if found:
            return sorted(found)
        nxt = set()
        for t in level:
            for i in range(len(t)):
                if t[i] in '()':
                    nxt.add(t[:i] + t[i + 1:])
        if not nxt:
            return [""]
        level = nxt
