import math


def covarianceAndCorrelation(X, ddof):
    n, d = len(X), len(X[0])
    cols = [[row[j] for row in X] for j in range(d)]
    constant = [all(v == c[0] for v in c) for c in cols]
    means = [c[0] if k else math.fsum(c) / n for c, k in zip(cols, constant)]   # exact for a constant column
    dev = [[v - m for v in c] for c, m in zip(cols, means)]          # two-pass: center first
    cov = [[math.fsum(p * q for p, q in zip(dev[i], dev[j])) / (n - ddof) for j in range(d)] for i in range(d)]
    corr = [[0.0 if constant[i] or constant[j] else cov[i][j] / math.sqrt(cov[i][i] * cov[j][j])
             for j in range(d)] for i in range(d)]
    return [cov, corr]
