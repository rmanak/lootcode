def tallestBillboard(rods):
    dp = {0: 0}
    for r in rods:
        cur = {}
        for d, t in dp.items():
            cur[d] = max(cur.get(d, 0), t)
            cur[d + r] = max(cur.get(d + r, 0), t + r)
            nd = abs(d - r)
            cur[nd] = max(cur.get(nd, 0), t + max(0, r - d))
        dp = cur
    return dp[0]
