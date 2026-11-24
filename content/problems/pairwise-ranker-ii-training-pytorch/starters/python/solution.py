import torch


def trainRanker(preferences, lr, steps):
    """Train a pairwise linear ranker with gradient descent from w = 0.

    Args:
        preferences: float32 tensor, shape (num_pairs, 2, num_features).
            Preferences[i] = [x1, x2], with x1 preferred over x2.
        lr: float. Learning rate.
        steps: int. Number of gradient-descent steps.

    Returns:
        A single float32 tensor: the learned weight vector w.
    """
    pass
