import math


def _merge(blocks):
    live = [b for b in blocks if b[0] is not None]       # a fully masked block contributes nothing
    d = len(blocks[0][2])
    if not live:
        return [None, 0.0, None, [0.0] * d]
    m = max(b[0] for b in live)                          # the new running max
    weights = [l * math.exp(mi - m) for mi, l, _ in live]  # each block's mass, rescaled to the new max
    l = sum(weights)
    o = [sum(w * b[2][j] for w, b in zip(weights, live)) / l for j in range(d)]
    return [m, l, m + math.log(l), o]


def mergeSoftmaxBlocks(queries):
    return [_merge(blocks) for blocks in queries]
