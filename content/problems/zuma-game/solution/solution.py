def findMinStep(board, hand):
    from collections import deque

    def remove(s):
        i = 0
        while i < len(s):
            j = i
            while j < len(s) and s[j] == s[i]:
                j += 1
            if j - i >= 3:
                s = s[:i] + s[j:]
                i = 0
            else:
                i = j
        return s

    start = (board, "".join(sorted(hand)))
    seen = {start}
    q = deque([(start[0], start[1], 0)])
    while q:
        b, h, steps = q.popleft()
        if b == "":
            return steps
        for i in range(len(b) + 1):
            for j in range(len(h)):
                if j > 0 and h[j] == h[j - 1]:
                    continue
                nb = remove(b[:i] + h[j] + b[i:])
                nh = h[:j] + h[j + 1:]
                state = (nb, nh)
                if state not in seen:
                    seen.add(state)
                    q.append((nb, nh, steps + 1))
    return -1
