def smallestSufficientTeamSize(req_skills, people):
    n = len(req_skills)
    sid = {s: i for i, s in enumerate(req_skills)}
    full = (1 << n) - 1
    INF = float('inf')
    dp = [INF] * (1 << n)
    dp[0] = 0
    pmasks = []
    for p in people:
        m = 0
        for s in p:
            if s in sid:
                m |= 1 << sid[s]
        pmasks.append(m)
    for mask in range(1 << n):
        if dp[mask] == INF:
            continue
        for pm in pmasks:
            nm = mask | pm
            if dp[nm] > dp[mask] + 1:
                dp[nm] = dp[mask] + 1
    return dp[full]
