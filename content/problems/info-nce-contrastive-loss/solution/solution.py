import numpy as np


def _softmax(S, axis):
    E = np.exp(S - S.max(axis=axis, keepdims=True))     # shift: exponents <= 0
    return E / E.sum(axis=axis, keepdims=True)


def _log_softmax_diag(S, axis):
    m = S.max(axis=axis, keepdims=True)
    lse = (m + np.log(np.exp(S - m).sum(axis=axis, keepdims=True))).ravel()
    return np.diag(S) - lse


def infoNCE(U, V, temperature):
    U = np.asarray(U, dtype=float)                      # (N, d) image embeddings
    V = np.asarray(V, dtype=float)                      # (N, d) text embeddings
    n = U.shape[0]
    nu = np.linalg.norm(U, axis=1, keepdims=True)
    nv = np.linalg.norm(V, axis=1, keepdims=True)
    Uh, Vh = U / nu, V / nv
    S = Uh @ Vh.T / temperature                         # S[i][j]: image i vs text j
    loss = -(_log_softmax_diag(S, 1).mean() + _log_softmax_diag(S, 0).mean()) / 2

    eye = np.eye(n)
    dS = ((_softmax(S, 1) - eye) + (_softmax(S, 0) - eye)) / (2 * n)
    dUh = dS @ Vh / temperature
    dVh = dS.T @ Uh / temperature
    # Back through x / |x|: remove the radial component, divide by the norm.
    dU = (dUh - Uh * (Uh * dUh).sum(axis=1, keepdims=True)) / nu
    dV = (dVh - Vh * (Vh * dVh).sum(axis=1, keepdims=True)) / nv
    return [float(loss), dU.tolist(), dV.tolist()]
