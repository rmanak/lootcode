import torch


def logisticRegressionGD(X, y, lr, steps):
    """Fit binary logistic regression with full-batch gradient descent.

    Args:
        X: float32 tensor, shape (num_samples, num_features). One sample per
            row.
        y: int64 tensor, shape (num_samples,). Labels, each 0 or 1.
        lr: float. Learning rate.
        steps: int. Number of gradient-descent steps.

    Returns:
        A list [w, b, lossHistory] (a tuple works too):
            w: float32 tensor. Learned weights.
            b: 0-dim float32 tensor. Learned bias.
            lossHistory: float32 tensor. Loss recorded at every step.
    """
    pass
