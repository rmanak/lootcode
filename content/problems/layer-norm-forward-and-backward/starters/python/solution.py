import numpy as np


def layerNormForwardBackward(x, gamma, beta, dy, eps):
    """Layer norm forward and backward pass.

    Args:
        x: list of lists of floats, shape (batch_size, num_features). Input,
            normalized per row.
        gamma: list of floats, shape (num_features,). Scale.
        beta: list of floats, shape (num_features,). Shift.
        dy: list of lists of floats, shape (batch_size, num_features). Upstream
            gradient dLoss/dy.
        eps: float. Added to the variance for stability.

    Returns:
        A list [y, dx, dgamma, dbeta] (a tuple works too):
            y: np.ndarray of floats. Normalized output.
            dx: np.ndarray of floats. Gradient w.r.t. x.
            dgamma: np.ndarray of floats. Gradient w.r.t. gamma.
            dbeta: np.ndarray of floats. Gradient w.r.t. beta.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
