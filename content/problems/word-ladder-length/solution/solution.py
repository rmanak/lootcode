def ladderLength(beginWord, endWord, wordList):
    from collections import deque
    words = set(wordList)
    if endWord not in words:
        return 0
    q = deque([(beginWord, 1)])
    seen = {beginWord}
    while q:
        w, d = q.popleft()
        if w == endWord:
            return d
        for i in range(len(w)):
            for c in "abcdefghijklmnopqrstuvwxyz":
                nxt = w[:i] + c + w[i + 1:]
                if nxt in words and nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, d + 1))
    return 0
