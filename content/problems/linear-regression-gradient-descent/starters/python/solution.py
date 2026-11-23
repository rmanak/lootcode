import numpy as np


def linearRegressionGD(X, y, lr, steps):
    """Fit linear regression (MSE) with full-batch gradient descent.

    Args:
        X: list of lists of floats, shape (num_samples, num_features). One
            sample per row.
        y: list of floats, shape (num_samples,). Regression targets.
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
