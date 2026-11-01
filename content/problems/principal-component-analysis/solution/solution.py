import numpy as np


def pca(X, k):
    X = np.asarray(X, dtype=float)                 # (N, d)
    Xc = X - X.mean(axis=0)                        # center every feature
    cov = Xc.T @ Xc / (len(X) - 1)                 # sample covariance, d x d
    vals, vecs = np.linalg.eigh(cov)               # ascending; columns are unit eigenvectors
    top = np.argsort(vals)[::-1][:k]               # the k largest
    comps = vecs[:, top].T                         # (k, d): one component per row
    # An eigenvector is only defined up to sign: flip each so that its entry
    # of largest magnitude is positive.
    big = np.argmax(np.abs(comps), axis=1)
    comps *= np.sign(comps[np.arange(k), big])[:, None]
    return [comps.tolist(), (Xc @ comps.T).tolist(), vals[top].tolist()]
