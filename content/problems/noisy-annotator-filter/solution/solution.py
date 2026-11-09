from collections import Counter


def _majority(labels):
    counts = Counter(labels)
    top = max(counts.values())
    return min(l for l, c in counts.items() if c == top)


def filterAnnotators(annotations, threshold):
    A = len(annotations[0])
    agree, seen = [0] * A, [0] * A
    for row in annotations:
        given = [(a, l) for a, l in enumerate(row) if l >= 0]
        for a, l in given:
            others = [m for b, m in given if b != a]
            if others:
                seen[a] += 1
                agree[a] += l == _majority(others)
    rates = [agree[a] / seen[a] if seen[a] else -1.0 for a in range(A)]
    bad = [a for a in range(A) if seen[a] and rates[a] < threshold]
    good = set(range(A)) - set(bad)
    labels = []
    for row in annotations:
        kept = [l for a, l in enumerate(row) if l >= 0 and a in good]
        labels.append(_majority(kept) if kept else -1)
    return [rates, bad, labels]
