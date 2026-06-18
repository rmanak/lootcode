def peopleIndexes(favoriteCompanies):
    sets = [set(f) for f in favoriteCompanies]
    n = len(sets)
    res = []
    for i in range(n):
        if not any(i != j and sets[i] <= sets[j] for j in range(n)):
            res.append(i)
    return res
