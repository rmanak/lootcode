import numpy as np


def smoothedMaskedCrossEntropy(logits, targets, mask, smoothing):
    z = np.asarray(logits, float)
    y = np.asarray(targets)
    m = np.asarray(mask, float)
    N, C = z.shape
    M = m.sum()
    if M == 0:
        return [0.0, np.zeros_like(z)]
    shifted = z - z.max(axis=1, keepdims=True)
    logp = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
    q = np.full((N, C), smoothing / C)
    q[np.arange(N), y] += 1 - smoothing
    per_position = -(q * logp).sum(axis=1)
    loss = (per_position * m).sum() / M
    grad = (np.exp(logp) - q) * (m / M)[:, None]
    return [float(loss), grad]
