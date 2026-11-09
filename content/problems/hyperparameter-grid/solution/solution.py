def gridLookup(values, queries):
    count = 1
    for opts in values:
        count *= len(opts)
    out = []
    for k in queries:
        combo = [None] * len(values)
        for t in range(len(values) - 1, -1, -1):    # the last key is the fastest digit
            k, d = divmod(k, len(values[t]))
            combo[t] = values[t][d]
        out.append(combo)
    return [count, out]
