def predictPartyVictory(senate):
    from collections import deque
    n = len(senate)
    R = deque()
    D = deque()
    for i, c in enumerate(senate):
        (R if c == 'R' else D).append(i)
    while R and D:
        r = R.popleft()
        d = D.popleft()
        if r < d:
            R.append(r + n)
        else:
            D.append(d + n)
    return "Radiant" if R else "Dire"
