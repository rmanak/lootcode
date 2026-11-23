import torch


def denseBackward(X, W, b, dY, activation):
    """X: (N, Din), W: (Din, Dout), b: (Dout,), dY: (N, Dout) float tensors;
    activation: "linear" | "relu" | "tanh" | "sigmoid".
    Return [dX, dW, db] as tensors of the inputs' dtype."""
    pass
