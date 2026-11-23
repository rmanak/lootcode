import numpy as np


def rankingLossAndGrad(preferences, w):
    """Mean pairwise logistic ranking loss and its gradient.

    Args:
        preferences: nested list of floats, shape (num_pairs, 2, num_features).
            Preferences[i] = [x1, x2], with x1 preferred over x2.
        w: list of floats, shape (num_features,). Weight vector.

    Returns:
        A list [L, grad] (a tuple works too):
            L: float. Mean loss over the pairs.
            grad: np.ndarray of floats. Gradient w.r.t. w.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
