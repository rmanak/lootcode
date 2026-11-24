import torch


def mlpBackprop(X, y, W1, b1, W2, b2):
    """Loss and gradients of a two-layer ReLU MLP with softmax cross-entropy.

    Args:
        X: float32 tensor, shape (batch_size, in_dim). Inputs.
        y: int64 tensor, shape (batch_size,). Class labels.
        W1: float32 tensor, shape (in_dim, hidden_dim). First-layer weights.
        b1: float32 tensor, shape (hidden_dim,). First-layer bias.
        W2: float32 tensor, shape (hidden_dim, num_classes). Second-layer
            weights.
        b2: float32 tensor, shape (num_classes,). Second-layer bias.

    Returns:
        A list [L, dW1, db1, dW2, db2] (a tuple works too):
            L: 0-dim float32 tensor. Mean loss over the batch.
            dW1: float32 tensor. Gradient w.r.t. W1.
            db1: float32 tensor. Gradient w.r.t. b1.
            dW2: float32 tensor. Gradient w.r.t. W2.
            db2: float32 tensor. Gradient w.r.t. b2.
    """
    pass
