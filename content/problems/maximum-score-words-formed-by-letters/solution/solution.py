def maxScoreWords(words, letters, score):
    from collections import Counter
    avail = Counter(letters)
    n = len(words)
    best = [0]

    def bt(i, remaining, cur):
        if i == n:
            best[0] = max(best[0], cur)
            return
        bt(i + 1, remaining, cur)
        wc = Counter(words[i])
        if all(remaining.get(c, 0) >= cnt for c, cnt in wc.items()):
            for c, cnt in wc.items():
                remaining[c] -= cnt
            ws = sum(score[ord(c) - 97] for c in words[i])
            bt(i + 1, remaining, cur + ws)
            for c, cnt in wc.items():
                remaining[c] += cnt

    bt(0, dict(avail), 0)
    return best[0]
