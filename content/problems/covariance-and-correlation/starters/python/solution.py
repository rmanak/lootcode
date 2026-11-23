import math

import numpy as np


def covarianceAndCorrelation(X, ddof):
    """Covariance and correlation matrices of a data matrix.

    Args:
        X: list of lists of floats, shape (num_samples, num_features). One
            sample per row.
        ddof: int. Delta degrees of freedom, 0 or 1.

    Returns:
        A list [cov, corr] (a tuple works too):
            cov: np.ndarray of floats. Covariance matrix.
            corr: np.ndarray of floats. Correlation matrix.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
