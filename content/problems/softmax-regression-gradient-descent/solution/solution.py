import numpy as np


def softmaxRegressionGD(X, y, numClasses, lr, steps):
    X = np.asarray(X, dtype=float)              # (N, d)
    y = np.asarray(y, dtype=int)
    n, d = X.shape
    Y = np.zeros((n, numClasses))
    Y[np.arange(n), y] = 1.0                    # one-hot labels
    W = np.zeros((d, numClasses))
    b = np.zeros(numClasses)
    history = []
    for _ in range(steps):
        Z = X @ W + b                           # logits (N, C)
        Z = Z - Z.max(axis=1, keepdims=True)    # stable: the largest logit is 0
        log_norm = np.log(np.exp(Z).sum(axis=1, keepdims=True))
        log_p = Z - log_norm                    # log-softmax, never log(0)
        history.append(float(-log_p[np.arange(n), y].mean()))
        G = (np.exp(log_p) - Y) / n             # dL/dZ for the mean loss
        W = W - lr * (X.T @ G)
        b = b - lr * G.sum(axis=0)
    return [W.tolist(), b.tolist(), history]
