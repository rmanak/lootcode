def maxLength(arr):
    masks = [0]
    best = 0
    for s in arr:
        if len(set(s)) != len(s):
            continue
        m = 0
        ok = True
        for ch in s:
            b = 1 << (ord(ch) - 97)
            if m & b:
                ok = False
                break
            m |= b
        if not ok:
            continue
        for prev in masks[:]:
            if prev & m:
                continue
            comb = prev | m
            masks.append(comb)
            best = max(best, bin(comb).count("1"))
    return best
