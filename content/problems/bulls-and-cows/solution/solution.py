def getHint(secret, guess):
    from collections import Counter
    bulls = sum(1 for s, g in zip(secret, guess) if s == g)
    sc = Counter(s for s, g in zip(secret, guess) if s != g)
    gc = Counter(g for s, g in zip(secret, guess) if s != g)
    cows = sum(min(sc[d], gc[d]) for d in sc)
    return f"{bulls}A{cows}B"
