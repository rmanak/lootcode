"""Input-constraint validator for problem 'context-window-packing'.

Hand-written. budget an int in [1, 20000]; minTokens an int in [1, 2000];
documents 1..200 entries [docId, score, tokens] with docId a str (distinct),
score a finite number (not a bool) in [0, 1000], tokens an int in [1, 2000].
"""
import math


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_input(budget, minTokens, documents):
    if not (_int(budget) and 1 <= budget <= 20000 and _int(minTokens) and 1 <= minTokens <= 2000):
        return False
    if not isinstance(documents, list) or not 1 <= len(documents) <= 200:
        return False
    ids = set()
    for d in documents:
        if not isinstance(d, list) or len(d) != 3:
            return False
        i, s, t = d
        if not isinstance(i, str) or i in ids:
            return False
        ids.add(i)
        if not isinstance(s, (int, float)) or isinstance(s, bool) or not math.isfinite(s) or not 0 <= s <= 1000:
            return False
        if not (_int(t) and 1 <= t <= 2000):
            return False
    return True
