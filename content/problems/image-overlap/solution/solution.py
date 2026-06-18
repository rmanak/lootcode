def largestOverlap(img1, img2):
    from collections import Counter
    n = len(img1)
    ones1 = [(i, j) for i in range(n) for j in range(n) if img1[i][j] == 1]
    ones2 = [(i, j) for i in range(n) for j in range(n) if img2[i][j] == 1]
    cnt = Counter()
    for i1, j1 in ones1:
        for i2, j2 in ones2:
            cnt[(i1 - i2, j1 - j2)] += 1
    return max(cnt.values()) if cnt else 0
