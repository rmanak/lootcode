import torch


def covarianceAndCorrelation(X, ddof):
    """Covariance and correlation matrices of a data matrix.

    Args:
        X: float64 tensor, shape (num_samples, num_features). One sample per
            row.
        ddof: int. Delta degrees of freedom, 0 or 1.

    Returns:
        A list [cov, corr] (a tuple works too):
            cov: float64 tensor. Covariance matrix.
            corr: float64 tensor. Correlation matrix.
    """
    pass
