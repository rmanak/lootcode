def numWays(s):
    MOD = 10 ** 9 + 7
    total = s.count('1')
    n = len(s)
    if total % 3 != 0:
        return 0
    if total == 0:
        return (n - 1) * (n - 2) // 2 % MOD
    each = total // 3
    ones = [i for i, c in enumerate(s) if c == '1']
    way1 = ones[each] - ones[each - 1]
    way2 = ones[2 * each] - ones[2 * each - 1]
    return (way1 * way2) % MOD
