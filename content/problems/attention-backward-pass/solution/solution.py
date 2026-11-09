import numpy as np


def attentionBackward(Q, K, V, dO, causal):
    Q = np.asarray(Q, float)
    K = np.asarray(K, float)
    V = np.asarray(V, float)
    dO = np.asarray(dO, float)
    scale = 1.0 / np.sqrt(Q.shape[1])
    S = Q @ K.T * scale
    if causal:
        S = np.where(np.tril(np.ones(S.shape, bool)), S, -np.inf)
    S = S - S.max(axis=1, keepdims=True)
    E = np.exp(S)
    P = E / E.sum(axis=1, keepdims=True)
    O = P @ V
    dV = P.T @ dO
    dP = dO @ V.T
    dS = P * (dP - (dP * P).sum(axis=1, keepdims=True))   # softmax backward, row by row
    dQ = dS @ K * scale
    dK = dS.T @ Q * scale
    return [O, dQ, dK, dV]
