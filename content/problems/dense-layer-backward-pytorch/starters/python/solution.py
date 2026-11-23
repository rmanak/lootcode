import torch


def denseBackward(X, W, b, dY, activation):
    """Backward pass of a dense layer Y = activation(X @ W + b).

    Args:
        X: float64 tensor, shape (batch_size, in_features). Layer input.
        W: float64 tensor, shape (in_features, out_features). Weights.
        b: float64 tensor, shape (out_features,). Bias.
        dY: float64 tensor, shape (batch_size, out_features). Upstream gradient
            dLoss/dY.
        activation: str. "linear", "relu", "tanh" or "sigmoid".

    Returns:
        A list [dX, dW, db] (a tuple works too):
            dX: float64 tensor. Gradient w.r.t. X.
            dW: float64 tensor. Gradient w.r.t. W.
            db: float64 tensor. Gradient w.r.t. b.
    """
    pass
