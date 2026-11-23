import numpy as np


def mlpBackprop(X, y, W1, b1, W2, b2):
    """Loss and gradients of a two-layer ReLU MLP with softmax cross-entropy.

    Args:
        X: list of lists of floats, shape (batch_size, in_dim). Inputs.
        y: list of ints, shape (batch_size,). Class labels.
        W1: list of lists of floats, shape (in_dim, hidden_dim). First-layer
            weights.
        b1: list of floats, shape (hidden_dim,). First-layer bias.
        W2: list of lists of floats, shape (hidden_dim, num_classes).
            Second-layer weights.
        b2: list of floats, shape (num_classes,). Second-layer bias.

    Returns:
        A list [L, dW1, db1, dW2, db2] (a tuple works too):
            L: float. Mean loss over the batch.
            dW1: np.ndarray of floats. Gradient w.r.t. W1.
            db1: np.ndarray of floats. Gradient w.r.t. b1.
            dW2: np.ndarray of floats. Gradient w.r.t. W2.
            db2: np.ndarray of floats. Gradient w.r.t. b2.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
