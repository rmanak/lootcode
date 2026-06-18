def recoverFromPreorder(traversal):
    s = traversal
    tokens = []
    i = 0
    while i < len(s):
        d = 0
        while i < len(s) and s[i] == "-":
            d += 1; i += 1
        j = i
        while j < len(s) and s[j].isdigit():
            j += 1
        tokens.append((d, int(s[i:j])))
        i = j
    val, left, right = {}, {}, {}
    stack = []
    nid = 0
    for d, v in tokens:
        node = nid; nid += 1
        val[node] = v
        while stack and stack[-1][0] >= d:
            stack.pop()
        if stack:
            parent = stack[-1][1]
            if parent not in left:
                left[parent] = node
            else:
                right[parent] = node
        stack.append((d, node))
    from collections import deque
    out = [val[0]]
    q = deque([0])
    while q:
        node = q.popleft()
        for ch in (left.get(node), right.get(node)):
            if ch is None:
                out.append(None)
            else:
                out.append(val[ch]); q.append(ch)
    while out and out[-1] is None:
        out.pop()
    return out
