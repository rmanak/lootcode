def sessionize(events, gap):
    cur = {}
    sessions = []
    for user, t in events:
        if user in cur and t - cur[user][1] <= gap:
            cur[user][1] = t
        else:
            if user in cur:
                sessions.append([user, [cur[user][0], cur[user][1]]])
            cur[user] = [t, t]
    for user, (s, e) in cur.items():
        sessions.append([user, [s, e]])
    sessions.sort(key=lambda x: (x[1][0], x[1][1], x[0]))
    return sessions
