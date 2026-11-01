import numpy as np


def ridgeRegression(X, y, lam):
    X = np.asarray(X, dtype=float)          # (N, d)
    y = np.asarray(y, dtype=float)
    # The intercept is not penalized. Centering removes it from the problem:
    # solve for w on centered data, then put the intercept back.
    x_mean, y_mean = X.mean(axis=0), y.mean()
    Xc, yc = X - x_mean, y - y_mean
    A = Xc.T @ Xc + lam * np.eye(X.shape[1])
    w = np.linalg.solve(A, Xc.T @ yc)
    b = y_mean - x_mean @ w
    return [w.tolist(), float(b)]
