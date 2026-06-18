def minWindow(s, t):
    if not t or len(t) > len(s):
        return ""
    from collections import Counter
    need = Counter(t)
    missing = len(t)
    left = start = end = 0
    best_len = float("inf")
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            if right - left + 1 < best_len:
                best_len = right - left + 1
                start, end = left, right + 1
            need[s[left]] += 1
            if need[s[left]] > 0:
                missing += 1
            left += 1
    return s[start:end] if best_len != float("inf") else ""
