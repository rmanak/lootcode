import numpy as np


def batchNormTrain(x, gamma, beta, dy, eps, runningMean, runningVar, momentum):
    x = np.asarray(x, dtype=float)              # (N, D): statistics are per column (feature)
    gamma = np.asarray(gamma, dtype=float)
    dy = np.asarray(dy, dtype=float)
    n = x.shape[0]
    mu = x.mean(axis=0)
    xc = x - mu
    var = (xc * xc).mean(axis=0)                # biased: divide by N (two-pass, so no cancellation)
    inv_std = 1.0 / np.sqrt(var + eps)
    xhat = xc * inv_std
    y = gamma * xhat + np.asarray(beta, dtype=float)

    dbeta = dy.sum(axis=0)
    dgamma = (dy * xhat).sum(axis=0)
    dxhat = dy * gamma
    dx = inv_std / n * (n * dxhat - dxhat.sum(axis=0) - xhat * (dxhat * xhat).sum(axis=0))

    # Running statistics, PyTorch convention: the running variance uses the
    # unbiased batch variance (divide by N - 1).
    new_mean = (1 - momentum) * np.asarray(runningMean, dtype=float) + momentum * mu
    new_var = (1 - momentum) * np.asarray(runningVar, dtype=float) + momentum * var * n / (n - 1)
    return [y.tolist(), dx.tolist(), dgamma.tolist(), dbeta.tolist(), new_mean.tolist(), new_var.tolist()]
