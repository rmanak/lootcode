import numpy as np


def multinomialNB(trainX, trainY, testX, alpha):
    X = np.asarray(trainX, dtype=float)         # (N, V) word counts
    y = np.asarray(trainY, dtype=int)
    T = np.asarray(testX, dtype=float)          # (M, V)
    C = int(y.max()) + 1
    V = X.shape[1]
    counts = np.zeros((C, V))
    np.add.at(counts, y, X)                     # word counts per class
    log_prior = np.log(np.bincount(y, minlength=C) / len(y))
    log_theta = np.log(counts + alpha) - np.log(counts.sum(axis=1, keepdims=True) + alpha * V)
    joint = T @ log_theta.T + log_prior         # (M, C) log P(c) + log P(x | c), up to a constant
    m = joint.max(axis=1, keepdims=True)
    log_norm = m + np.log(np.exp(joint - m).sum(axis=1, keepdims=True))
    preds = joint.argmax(axis=1)                # argmax returns the first (smallest) class on a tie
    return [preds.tolist(), (joint - log_norm).tolist()]
