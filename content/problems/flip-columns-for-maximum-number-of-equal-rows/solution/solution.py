def maxEqualRowsAfterFlips(matrix):
    from collections import Counter
    cnt = Counter()
    for row in matrix:
        key = tuple(c ^ row[0] for c in row)
        cnt[key] += 1
    return max(cnt.values())
