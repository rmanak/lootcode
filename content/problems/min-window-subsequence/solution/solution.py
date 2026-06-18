def minWindow(s, t):
    n, m = len(s), len(t)
    best_len = float('inf')
    best_start = -1
    i = 0
    while i < n:
        j = 0
        k = i
        while k < n:
            if s[k] == t[j]:
                j += 1
                if j == m:
                    break
            k += 1
        if j < m:
            break
        end = k
        j = m - 1
        while True:
            if s[k] == t[j]:
                j -= 1
                if j < 0:
                    break
            k -= 1
        start = k
        if end - start + 1 < best_len:
            best_len = end - start + 1
            best_start = start
        i = start + 1
    return "" if best_start < 0 else s[best_start:best_start + best_len]
