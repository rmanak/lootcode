import numpy as np


def _log_softmax(z):
    z = z - z.max(axis=1, keepdims=True)
    return z - np.log(np.exp(z).sum(axis=1, keepdims=True))


def spanLossAndDecode(startLogits, endLogits, goldStarts, goldEnds, maxLen):
    s = np.asarray(startLogits, float)
    e = np.asarray(endLogits, float)
    B, T = s.shape
    rows = np.arange(B)
    ls, le = _log_softmax(s), _log_softmax(e)
    loss = float(-(ls[rows, goldStarts] + le[rows, goldEnds]).mean() / 2)
    i = np.arange(T)
    valid = (i[None, :] >= i[:, None]) & (i[None, :] - i[:, None] < maxLen)   # [start, end]
    spans = []
    for b in range(B):
        score = np.where(valid, s[b][:, None] + e[b][None, :], -np.inf)
        k = int(np.argmax(score))          # row-major: smallest start, then smallest end
        spans.append([k // T, k % T])
    return [loss, spans]
