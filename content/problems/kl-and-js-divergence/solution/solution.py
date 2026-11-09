import numpy as np


def _kl(a, b):
    nz = a > 0
    return float(np.sum(a[nz] * (np.log(a[nz]) - np.log(b[nz]))))


def divergences(p, q):
    P = np.asarray(p, float)
    Q = np.asarray(q, float)
    P = P / P.sum()
    Q = Q / Q.sum()
    M = (P + Q) / 2
    return [_kl(P, Q), _kl(Q, P), 0.5 * _kl(P, M) + 0.5 * _kl(Q, M)]
