import torch


def layerNormForwardBackward(x, gamma, beta, dy, eps):
    """Layer norm forward and backward pass.

    Args:
        x: float64 tensor, shape (batch_size, num_features). Input, normalized
            per row.
        gamma: float64 tensor, shape (num_features,). Scale.
        beta: float64 tensor, shape (num_features,). Shift.
        dy: float64 tensor, shape (batch_size, num_features). Upstream gradient
            dLoss/dy.
        eps: float. Added to the variance for stability.

    Returns:
        A list [y, dx, dgamma, dbeta] (a tuple works too):
            y: float64 tensor. Normalized output.
            dx: float64 tensor. Gradient w.r.t. x.
            dgamma: float64 tensor. Gradient w.r.t. gamma.
            dbeta: float64 tensor. Gradient w.r.t. beta.
    """
    pass
