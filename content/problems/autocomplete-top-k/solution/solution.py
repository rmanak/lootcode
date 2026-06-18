def autocomplete(k, operations):
    freq, out = {}, []
    for op in operations:
        if op[0] == "add":
            s, c = op[1], op[2]
            freq[s] = freq.get(s, 0) + c
            out.append(None)
        else:
            prefix = op[1]
            cands = [s for s in freq if s.startswith(prefix)]
            cands.sort(key=lambda s: (-freq[s], s))
            out.append(cands[:k])
    return out
