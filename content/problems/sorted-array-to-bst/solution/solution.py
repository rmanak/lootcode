class _N:
    __slots__ = ("v", "l", "r")

    def __init__(self, v):
        self.v, self.l, self.r = v, None, None


def _build(arr):
    if not arr or arr[0] is None:
        return None
    root = _N(arr[0])
    q, i = [root], 1
    while q and i < len(arr):
        cur = q.pop(0)
        if i < len(arr):
            x = arr[i]; i += 1
            if x is not None:
                cur.l = _N(x); q.append(cur.l)
        if i < len(arr):
            x = arr[i]; i += 1
            if x is not None:
                cur.r = _N(x); q.append(cur.r)
    return root


def _ser(root):
    out, q = [], [root]
    while q:
        node = q.pop(0)
        if node is None:
            out.append(None)
            continue
        out.append(node.v)
        q.append(node.l)
        q.append(node.r)
    while out and out[-1] is None:
        out.pop()
    return out


def sortedArrayToBST(nums):
    def build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        node = _N(nums[mid])
        node.l = build(lo, mid - 1)
        node.r = build(mid + 1, hi)
        return node

    return _ser(build(0, len(nums) - 1))
