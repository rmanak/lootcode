def isSolvable(words, result):
    rows = words + [result]
    if any(len(w) > len(result) for w in words):
        return False
    L = len(result)
    leading = set(w[0] for w in rows if len(w) > 1)
    cols = []
    for i in range(L):
        wc = [w[-1 - i] for w in words if i < len(w)]
        rc = result[-1 - i]
        cols.append((wc, rc))
    assigned = {}
    used = [False] * 10

    def place(col, carry):
        if col == L:
            return carry == 0
        wc, rc = cols[col]

        def rec(k, s):
            if k == len(wc):
                total = s + carry
                d = total % 10
                nc = total // 10
                if rc in assigned:
                    if assigned[rc] != d or (d == 0 and rc in leading):
                        return False
                    return place(col + 1, nc)
                if used[d] or (d == 0 and rc in leading):
                    return False
                assigned[rc] = d
                used[d] = True
                ok = place(col + 1, nc)
                del assigned[rc]
                used[d] = False
                return ok
            ch = wc[k]
            if ch in assigned:
                return rec(k + 1, s + assigned[ch])
            for d in range(10):
                if used[d] or (d == 0 and ch in leading):
                    continue
                assigned[ch] = d
                used[d] = True
                if rec(k + 1, s + d):
                    del assigned[ch]
                    used[d] = False
                    return True
                del assigned[ch]
                used[d] = False
            return False

        return rec(0, 0)

    return place(0, 0)
