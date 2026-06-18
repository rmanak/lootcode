def isNStraightHand(hand, groupSize):
    from collections import Counter
    if len(hand) % groupSize != 0:
        return False
    cnt = Counter(hand)
    for x in sorted(cnt):
        c = cnt[x]
        if c > 0:
            for y in range(x, x + groupSize):
                if cnt[y] < c:
                    return False
                cnt[y] -= c
    return True
