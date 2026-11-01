import math


def clipGradients(grads, maxNorm):
    # Global L2 norm over every entry of every tensor. Divide by the largest
    # magnitude first, so squaring values near 1e200 cannot overflow.
    big = max(abs(v) for g in grads for v in g)
    if big == 0:
        norm = 0.0
    else:
        norm = big * math.sqrt(math.fsum((v / big) ** 2 for g in grads for v in g))
    if norm > maxNorm:
        scale = maxNorm / norm
        grads = [[v * scale for v in g] for g in grads]
    else:
        grads = [[float(v) for v in g] for g in grads]
    return [grads, norm]
