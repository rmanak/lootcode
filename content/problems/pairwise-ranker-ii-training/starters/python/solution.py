import numpy as np


def trainRanker(preferences, lr, steps):
    """preferences: list of N pairs [x1, x2] (x1 preferred), each a list of d numbers.
    Start at w = 0 and take exactly `steps` full-batch gradient-descent steps of
    size lr on the mean pairwise logistic loss. Return w (a numpy array is fine)."""
    pass
