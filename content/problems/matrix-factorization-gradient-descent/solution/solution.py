import numpy as np


def matrixFactorizationGD(ratings, U, V, lr, reg, steps):
    U = np.asarray(U, dtype=float).copy()       # (users, k)
    V = np.asarray(V, dtype=float).copy()       # (items, k)
    R = np.asarray(ratings, dtype=float).reshape(-1, 3)
    users, items, r = R[:, 0].astype(int), R[:, 1].astype(int), R[:, 2]
    history = []
    for _ in range(steps):
        err = np.einsum("nk,nk->n", U[users], V[items]) - r      # prediction - rating
        history.append(float(err @ err + reg * ((U * U).sum() + (V * V).sum())))
        gU = 2 * reg * U
        gV = 2 * reg * V
        np.add.at(gU, users, 2 * err[:, None] * V[items])        # several ratings can share a user
        np.add.at(gV, items, 2 * err[:, None] * U[users])
        U, V = U - lr * gU, V - lr * gV                          # both from the old U and V
    return [U.tolist(), V.tolist(), history]
