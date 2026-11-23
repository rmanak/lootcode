import torch


def divergences(p, q):
    """KL divergence both ways and the Jensen-Shannon divergence, in nats.

    Args:
        p: float64 tensor, shape (num_categories,). Non-negative weights (not
            yet normalized).
        q: float64 tensor, shape (num_categories,). Non-negative weights (not
            yet normalized).

    Returns:
        A single float64 tensor: the values [KL(P || Q), KL(Q || P), JS(P, Q)],
        in that order.
    """
    pass
