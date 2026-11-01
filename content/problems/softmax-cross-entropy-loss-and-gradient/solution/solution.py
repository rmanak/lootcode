import numpy as np


def softmaxCrossEntropy(logits, labels):
    z = np.asarray(logits, dtype=float)             # (N, C)
    rows = np.arange(len(z))
    y = np.asarray(labels, dtype=int)
    # Softmax ignores a constant added to a row, so shift each row's largest
    # logit to 0: every exponent is then <= 0 and nothing can overflow.
    shifted = z - z.max(axis=1, keepdims=True)
    # Stay in log space: log p = shifted - log(sum exp(shifted)). The sum is
    # >= 1, so this never takes the log of an underflowed probability.
    log_probs = shifted - np.log(np.exp(shifted).sum(axis=1, keepdims=True))
    loss = -log_probs[rows, y].mean()
    # d(loss)/d(logits) = (softmax - one_hot(labels)) / N
    grad = np.exp(log_probs)
    grad[rows, y] -= 1.0
    grad /= len(z)
    return float(loss), grad.tolist()
