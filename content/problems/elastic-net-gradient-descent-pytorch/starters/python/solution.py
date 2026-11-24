import torch


def elasticNetGD(X, y, alpha, l1Ratio, lr, steps):
    """Fit elastic-net linear regression with full-batch gradient descent.

    Args:
        X: float32 tensor, shape (num_samples, num_features). One sample per
            row.
        y: float32 tensor, shape (num_samples,). Regression targets.
        alpha: float. Overall penalty strength.
        l1Ratio: float. L1 share of the penalty, in [0, 1].
        lr: float. Learning rate.
        steps: int. Number of gradient-descent steps.

    Returns:
        A list [w, b, lossHistory] (a tuple works too):
            w: float32 tensor. Learned weights.
            b: 0-dim float32 tensor. Learned bias.
            lossHistory: float32 tensor. Loss recorded at every step.
    """
    pass
