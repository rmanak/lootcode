def canStamp(stamp, target):
    t = list(target)
    n, m = len(target), len(stamp)
    total = 0
    while total < n:
        progressed = False
        for i in range(n - m + 1):
            ok = True
            has_real = False
            for j in range(m):
                if t[i + j] == '*':
                    continue
                has_real = True
                if t[i + j] != stamp[j]:
                    ok = False
                    break
            if ok and has_real:
                for j in range(m):
                    if t[i + j] != '*':
                        t[i + j] = '*'
                        total += 1
                progressed = True
        if not progressed:
            break
    return total == n
