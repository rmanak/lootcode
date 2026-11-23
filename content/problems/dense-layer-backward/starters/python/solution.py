import numpy as np


def denseBackward(X, W, b, dY, activation):
    """Backward pass of a dense layer Y = activation(X @ W + b).

    Args:
        X: list of lists of floats, shape (batch_size, in_features). Layer
            input.
        W: list of lists of floats, shape (in_features, out_features). Weights.
        b: list of floats, shape (out_features,). Bias.
        dY: list of lists of floats, shape (batch_size, out_features). Upstream
            gradient dLoss/dY.
        activation: str. "linear", "relu", "tanh" or "sigmoid".

    Returns:
        A list [dX, dW, db] (a tuple works too):
            dX: np.ndarray of floats. Gradient w.r.t. X.
            dW: np.ndarray of floats. Gradient w.r.t. W.
            db: np.ndarray of floats. Gradient w.r.t. b.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
