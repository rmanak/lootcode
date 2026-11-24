import torch


def rankingLossAndGrad(preferences, w):
    """Mean pairwise logistic ranking loss and its gradient.

    Args:
        preferences: float32 tensor, shape (num_pairs, 2, num_features).
            Preferences[i] = [x1, x2], with x1 preferred over x2.
        w: float32 tensor, shape (num_features,). Weight vector.

    Returns:
        A list [L, grad] (a tuple works too):
            L: 0-dim float32 tensor. Mean loss over the pairs.
            grad: float32 tensor. Gradient w.r.t. w.
    """
    pass
