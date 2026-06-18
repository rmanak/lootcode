def bstFromPreorder(preorder):
    from collections import deque
    val = {0: preorder[0]}
    left, right = {}, {}
    nid = 0
    for v in preorder[1:]:
        nid += 1
        val[nid] = v
        cur = 0
        while True:
            if v < val[cur]:
                if cur in left:
                    cur = left[cur]
                else:
                    left[cur] = nid; break
            else:
                if cur in right:
                    cur = right[cur]
                else:
                    right[cur] = nid; break
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
