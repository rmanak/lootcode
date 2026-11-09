import numpy as np


def prefixProductsBackward(W, dP):
    W = np.asarray(W, float)
    G = np.asarray(dP, float)
    N, D, _ = W.shape
    P = np.empty_like(W)
    acc = np.eye(D)
    for i in range(N):
        acc = acc @ W[i]
        P[i] = acc
    # R_j = sum_{i >= j} dP_i (W_{j+1} ... W_i)^T, built from the back:
    # R_{N-1} = dP_{N-1},  R_j = dP_j + R_{j+1} W_{j+1}^T.  Then dW_j = P_{j-1}^T R_j.
    dW = np.empty_like(W)
    R = np.zeros((D, D))
    for j in range(N - 1, -1, -1):
        R = G[j] + (R @ W[j + 1].T if j + 1 < N else 0)
        left = P[j - 1] if j > 0 else np.eye(D)
        dW[j] = left.T @ R
    return [P, dW]
