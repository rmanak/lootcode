import numpy as np


def moeLayer(X, Wg, experts, k, capacity):
    X = np.asarray(X, dtype=float)              # (T, d)
    Wg = np.asarray(Wg, dtype=float)            # (d, E)
    W = np.asarray(experts, dtype=float)        # (E, d, d): expert e maps x -> x @ W[e]
    T, E = X.shape[0], Wg.shape[1]
    logits = X @ Wg                             # (T, E)

    # Top-k by logit, highest first; equal logits go to the lower expert index
    # (a stable sort on the negated logits keeps index order among ties).
    idx = np.argsort(-logits, axis=1, kind="stable")[:, :k]
    top = np.take_along_axis(logits, idx, axis=1)
    g = np.exp(top - top[:, :1])                # softmax over the k selected logits only
    gates = g / g.sum(axis=1, keepdims=True)

    out = np.zeros_like(X)
    load = [0] * E
    for t in range(T):                          # tokens in order, each token's choices in rank order
        for r in range(k):
            e = int(idx[t, r])
            if load[e] < capacity:              # a full expert drops the assignment: no output, no renormalizing
                load[e] += 1
                out[t] += gates[t, r] * (X[t] @ W[e])

    # Switch Transformer load-balancing loss.
    p = np.exp(logits - logits.max(axis=1, keepdims=True))
    p /= p.sum(axis=1, keepdims=True)           # router probabilities over all E experts
    f = np.bincount(idx[:, 0], minlength=E) / T # fraction of tokens whose top-1 is e
    aux = E * float(np.dot(f, p.mean(axis=0)))
    return [idx.tolist(), gates.tolist(), out.tolist(), load, aux]
