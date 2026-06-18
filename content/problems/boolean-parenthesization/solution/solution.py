def countWays(expr):
    from functools import lru_cache
    symbols = expr[0::2]
    ops = expr[1::2]
    n = len(symbols)

    @lru_cache(None)
    def solve(i, j, want):
        if i == j:
            return 1 if (symbols[i] == 'T') == want else 0
        total = 0
        for k in range(i, j):
            op = ops[k]
            lt, lf = solve(i, k, True), solve(i, k, False)
            rt, rf = solve(k + 1, j, True), solve(k + 1, j, False)
            tt, tf, ft, ff = lt * rt, lt * rf, lf * rt, lf * rf
            if op == '&':
                true_ways, false_ways = tt, tf + ft + ff
            elif op == '|':
                true_ways, false_ways = tt + tf + ft, ff
            else:
                true_ways, false_ways = tf + ft, tt + ff
            total += true_ways if want else false_ways
        return total

    return solve(0, n - 1, True)
