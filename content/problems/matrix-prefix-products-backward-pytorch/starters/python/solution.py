import torch


def prefixProductsBackward(W, dP):
    """Prefix products of a chain of matrices, and their backward pass.

    Args:
        W: float64 tensor, shape (num_matrices, dim, dim). The chain W[0],
            W[1], ...
        dP: float64 tensor, shape (num_matrices, dim, dim). Upstream gradient:
            dP[i] = dLoss/dP[i].

    Returns:
        A list [P, dW] (a tuple works too):
            P: float64 tensor. The prefix products.
            dW: float64 tensor. Gradient w.r.t. W.
    """
    pass
