import math
import re
from collections import Counter


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def tfidfSearch(documents, queries, k):
    docs = [Counter(tokenize(d)) for d in documents]
    n = len(docs)
    df = Counter(t for c in docs for t in c)
    idf = {t: math.log((1 + n) / (1 + df[t])) + 1.0 for t in df}   # smooth idf

    def vector(counts):
        v = {t: c * idf[t] for t, c in counts.items() if t in idf}  # unknown query words are dropped
        norm = math.sqrt(math.fsum(x * x for x in v.values()))
        return {t: x / norm for t, x in v.items()} if norm else {}

    dvecs = [vector(c) for c in docs]
    top_idx, top_scores = [], []
    for q in queries:
        qv = vector(Counter(tokenize(q)))
        # fsum is exactly rounded, so equal vectors give bit-identical scores.
        scores = [math.fsum(w * dv.get(t, 0.0) for t, w in qv.items()) for dv in dvecs]
        order = sorted(range(n), key=lambda i: (-scores[i], i))[:k]
        top_idx.append(order)
        top_scores.append([scores[i] for i in order])
    return [top_idx, top_scores]
