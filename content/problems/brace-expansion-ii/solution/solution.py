def braceExpansionII(expression):
    s = expression
    pos = [0]

    def parse():
        result = set()
        cur = {""}
        while pos[0] < len(s) and s[pos[0]] != "}":
            ch = s[pos[0]]
            if ch == "{":
                pos[0] += 1
                sub = parse()
                pos[0] += 1  # skip '}'
                cur = {a + b for a in cur for b in sub}
            elif ch == ",":
                pos[0] += 1
                result |= cur
                cur = {""}
            else:
                j = pos[0]
                while j < len(s) and s[j].isalpha():
                    j += 1
                token = s[pos[0]:j]
                pos[0] = j
                cur = {a + token for a in cur}
        result |= cur
        return result

    return sorted(parse())
