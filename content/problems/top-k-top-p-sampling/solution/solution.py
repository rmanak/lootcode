import numpy as np


def sampleToken(logits, temperature, topK, topP, u):
    z = np.asarray(logits, dtype=float) / temperature
    p = np.exp(z - z.max())                    # stable softmax
    p /= p.sum()
    ids = np.arange(len(p))
    order = np.lexsort((ids, -p))              # most likely first; equal: lower id first
    keep = order[:topK]                        # top-k
    q = p[keep] / p[keep].sum()                # renormalize over the top k
    cum = np.cumsum(q)
    n = int(np.searchsorted(cum, topP, side="left")) + 1   # first prefix with cum >= topP
    keep = keep[:min(n, len(keep))]            # top-p (nucleus)
    final = np.zeros_like(p)
    final[keep] = p[keep] / p[keep].sum()
    # Inverse CDF in token-id order: the first id whose running total exceeds u.
    cdf = np.cumsum(final)
    token = int(np.searchsorted(cdf, u, side="right"))
    if token >= len(p):                        # u above a total rounded just below 1
        token = int(keep.max())
    return [token, final.tolist()]
