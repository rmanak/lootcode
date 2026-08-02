def longestDupSubstring(s):
    n = len(s)
    MOD = (1 << 61) - 1
    BASE = 131

    # Rolling (Rabin-Karp) hashes: prefix[i] hashes s[:i], so any window's hash
    # is one multiply and one subtract. Binary search the length on top of that.
    pw = [1] * (n + 1)
    pref = [0] * (n + 1)
    for i, ch in enumerate(s):
        pw[i + 1] = pw[i] * BASE % MOD
        pref[i + 1] = (pref[i] * BASE + (ord(ch) - 96)) % MOD

    def has_dup(length):
        seen = {}
        p = pw[length]
        for i in range(n - length + 1):
            key = (pref[i + length] - pref[i] * p) % MOD
            bucket = seen.get(key)
            if bucket is None:
                seen[key] = [i]
            else:
                # A shared hash is almost always a real repeat; confirm it so a
                # collision can never produce a wrong answer.
                sub = s[i:i + length]
                for j in bucket:
                    if s[j:j + length] == sub:
                        return True
                bucket.append(i)
        return False

    lo, hi, best = 1, n - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if has_dup(mid):
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best
