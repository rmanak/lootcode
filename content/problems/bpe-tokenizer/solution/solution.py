from collections import Counter


def _merge(symbols, left, right):
    """Replace every occurrence of (left, right), scanning left to right."""
    out, i = [], 0
    while i < len(symbols):
        if i + 1 < len(symbols) and symbols[i] == left and symbols[i + 1] == right:
            out.append(left + right)
            i += 2
        else:
            out.append(symbols[i])
            i += 1
    return out


def bpeTokenize(corpus, numMerges, word):
    freq = Counter(corpus)                       # each distinct word, with its count
    words = {w: list(w) for w in freq}           # start from single characters
    merges = []
    for _ in range(numMerges):
        pairs = Counter()
        for w, syms in words.items():
            for a, b in zip(syms, syms[1:]):     # every adjacent position counts
                pairs[(a, b)] += freq[w]
        if not pairs:
            break
        top = max(pairs.values())
        best = min(p for p, c in pairs.items() if c == top)   # smallest (left, right)
        merges.append(list(best))
        words = {w: _merge(syms, *best) for w, syms in words.items()}
    tokens = list(word)
    for left, right in merges:                   # replay the merges in learned order
        tokens = _merge(tokens, left, right)
    return [merges, tokens]
