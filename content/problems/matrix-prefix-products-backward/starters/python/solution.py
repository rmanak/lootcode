import numpy as np


def prefixProductsBackward(W, dP):
    """Prefix products of a chain of matrices, and their backward pass.

    Args:
        W: nested list of floats, shape (num_matrices, dim, dim). The chain
            W[0], W[1], ...
        dP: nested list of floats, shape (num_matrices, dim, dim). Upstream
            gradient: dP[i] = dLoss/dP[i].

    Returns:
        A list [P, dW] (a tuple works too):
            P: np.ndarray of floats. The prefix products.
            dW: np.ndarray of floats. Gradient w.r.t. W.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
