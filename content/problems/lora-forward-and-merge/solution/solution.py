import math

import numpy as np


def loraForward(X, W, A, B, alpha, useRsLora):
    X = np.asarray(X, dtype=float)      # (N, din)
    W = np.asarray(W, dtype=float)      # (din, dout), frozen
    A = np.asarray(A, dtype=float)      # (din, r)
    B = np.asarray(B, dtype=float)      # (r, dout)
    r = A.shape[1]
    scaling = alpha / math.sqrt(r) if useRsLora else alpha / r
    Y = X @ W + scaling * ((X @ A) @ B)  # low-rank path: never forms the din x dout update
    W_merged = W + scaling * (A @ B)     # fold the adapter in for zero-overhead inference
    return [Y.tolist(), W_merged.tolist()]
