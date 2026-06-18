def streamChecker(words, queries):
    root = {}
    max_len = 0
    for w in words:
        node = root
        for ch in reversed(w):
            node = node.setdefault(ch, {})
        node["$"] = True
        max_len = max(max_len, len(w))
    from collections import deque
    stream = deque()
    out = []
    for q in queries:
        stream.appendleft(q)
        while len(stream) > max_len:
            stream.pop()
        node = root
        found = False
        for ch in stream:
            if ch not in node:
                break
            node = node[ch]
            if "$" in node:
                found = True
                break
        out.append(found)
    return out
