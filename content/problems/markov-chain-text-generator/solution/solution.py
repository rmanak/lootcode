import re
from collections import Counter, defaultdict


def generateText(corpus, startWord, steps, draws):
    words = re.sub(r"[^a-z0-9']", " ", corpus.lower()).split()
    followers = defaultdict(Counter)
    for a, b in zip(words, words[1:]):
        followers[a][b] += 1
    cur = startWord.lower()
    out = [cur]
    for t in range(steps):
        options = followers.get(cur)
        if not options:
            break
        if not draws:
            top = max(options.values())
            cur = min(w for w, c in options.items() if c == top)
        else:
            total = sum(options.values())
            acc = 0
            for w in sorted(options):
                acc += options[w]
                if draws[t] < acc / total:
                    cur = w
                    break
            else:                                  # guard against rounding at the top end
                cur = max(options)
        out.append(cur)
    return out
