import torch


def grpoLoss(rewards, newLogps, oldLogps, refLogps, clipEps, beta, aggregation):
    """rewards: (B, G) float64 tensor; newLogps, oldLogps, refLogps: lists of
    B*G float64 tensors, completion k's tokens (lengths differ, the three lists
    agree); clipEps, beta: float; aggregation: "sequence" or "token".
    Return [advantages, loss, clipFraction, meanKl]: advantages (B, G), the
    rest 0-dim, all float64."""
    pass
