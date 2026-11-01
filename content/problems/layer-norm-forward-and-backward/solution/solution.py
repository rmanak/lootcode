import numpy as np


def layerNormForwardBackward(x, gamma, beta, dy, eps):
    x = np.asarray(x, dtype=float)              # (N, D)
    gamma = np.asarray(gamma, dtype=float)      # (D,)
    beta = np.asarray(beta, dtype=float)
    dy = np.asarray(dy, dtype=float)
    mu = x.mean(axis=1, keepdims=True)
    xc = x - mu
    # Variance from the deviations (two passes), not mean(x²) - mu²: the latter
    # cancels catastrophically when a row has a large mean and a tiny spread.
    var = (xc * xc).mean(axis=1, keepdims=True)  # biased: divide by D
    inv_std = 1.0 / np.sqrt(var + eps)
    xhat = xc * inv_std
    y = gamma * xhat + beta
    dbeta = dy.sum(axis=0)
    dgamma = (dy * xhat).sum(axis=0)
    # Backward through the normalization, per row: the mean and the variance
    # both depend on every x in the row, which adds the two correction terms.
    g = dy * gamma
    dx = inv_std * (g - g.mean(axis=1, keepdims=True)
                    - xhat * (g * xhat).mean(axis=1, keepdims=True))
    return [y.tolist(), dx.tolist(), dgamma.tolist(), dbeta.tolist()]
