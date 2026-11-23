import math

import numpy as np


def divergences(p, q):
    """KL divergence both ways and the Jensen-Shannon divergence, in nats.

    Args:
        p: list of floats, shape (num_categories,). Non-negative weights (not
            yet normalized).
        q: list of floats, shape (num_categories,). Non-negative weights (not
            yet normalized).

    Returns:
        A list [klPQ, klQP, js] (a tuple works too):
            klPQ: float. KL(P || Q).
            klQP: float. KL(Q || P).
            js: float. JS(P, Q).
    """
    pass
