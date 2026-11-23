import torch


def covarianceAndCorrelation(X, ddof):
    cov = torch.cov(X.T, correction=ddof).reshape(X.shape[1], X.shape[1])
    constant = (X == X[0]).all(dim=0)               # zero variance: correlation undefined
    std = cov.diagonal().clamp(min=0).sqrt()
    corr = cov / (std[:, None] * std[None, :])
    corr = corr.masked_fill(constant[:, None] | constant[None, :], 0.0)
    cov = cov.masked_fill(constant[:, None] | constant[None, :], 0.0)
    return [cov, corr]
