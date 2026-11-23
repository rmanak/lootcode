import numpy as np


def elasticNetGD(X, y, alpha, l1Ratio, lr, steps):
    """Fit elastic-net linear regression with full-batch gradient descent.

    Args:
        X: list of lists of floats, shape (num_samples, num_features). One
            sample per row.
        y: list of floats, shape (num_samples,). Regression targets.
        alpha: float. Overall penalty strength.
        l1Ratio: float. L1 share of the penalty, in [0, 1].
        lr: float. Learning rate.
        steps: int. Number of gradient-descent steps.

    Returns:
        A list [w, b, lossHistory] (a tuple works too):
            w: np.ndarray of floats. Learned weights.
            b: float. Learned bias.
            lossHistory: np.ndarray of floats. Loss recorded at every step.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
