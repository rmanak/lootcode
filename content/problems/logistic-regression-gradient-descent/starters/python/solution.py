import numpy as np


def logisticRegressionGD(X, y, lr, steps):
    """Fit binary logistic regression with full-batch gradient descent.

    Args:
        X: list of lists of floats, shape (num_samples, num_features). One
            sample per row.
        y: list of ints, shape (num_samples,). Labels, each 0 or 1.
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
