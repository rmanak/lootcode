def rankTeams(votes):
    from collections import defaultdict
    m = len(votes[0])
    rank = defaultdict(lambda: [0] * m)
    for vote in votes:
        for i, team in enumerate(vote):
            rank[team][i] += 1
    teams = list(rank.keys())
    teams.sort(key=lambda t: (tuple(-c for c in rank[t]), t))
    return "".join(teams)
