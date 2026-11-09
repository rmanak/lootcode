"""Input-constraint validator for problem 'markov-chain-text-generator'.

Hand-written. corpus: str of 1..2e5 printable ASCII chars; startWord: a
non-empty str of [A-Za-z0-9']; steps an int in [0, 1000]; draws empty or
exactly `steps` numbers (not bools) in [0, 1). Also enforces the stated
promise that no draw lies within 1e-9 of a cumulative boundary of the
follower distribution it is used on (exact Fraction arithmetic).
"""
import re
from collections import Counter, defaultdict
from fractions import Fraction


def validate_input(corpus, startWord, steps, draws):
    if not isinstance(corpus, str) or not 1 <= len(corpus) <= 2 * 10**5:
        return False
    if not all(32 <= ord(c) < 127 or c in "\n\t" for c in corpus):
        return False
    if not isinstance(startWord, str) or not re.fullmatch(r"[A-Za-z0-9']+", startWord):
        return False
    if not isinstance(steps, int) or isinstance(steps, bool) or not 0 <= steps <= 1000:
        return False
    if not isinstance(draws, list) or (draws and len(draws) != steps):
        return False
    if not all(isinstance(u, (int, float)) and not isinstance(u, bool) and 0 <= u < 1 for u in draws):
        return False
    if not draws:
        return True
    words = re.sub(r"[^a-z0-9']", " ", corpus.lower()).split()
    fol = defaultdict(Counter)
    for a, b in zip(words, words[1:]):
        fol[a][b] += 1
    cur = startWord.lower()
    for u in draws:
        opts = fol.get(cur)
        if not opts:
            break
        total, acc = sum(opts.values()), 0
        fu = Fraction(u)
        nxt = None
        for w in sorted(opts):
            acc += opts[w]
            b = Fraction(acc, total)
            if abs(fu - b) < Fraction(1, 10**9) and acc < total:
                return False
            if nxt is None and fu < b:
                nxt = w
        cur = nxt
    return True
