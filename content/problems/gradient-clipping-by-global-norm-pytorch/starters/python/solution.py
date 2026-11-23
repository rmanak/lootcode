import torch


def clipGradients(grads, maxNorm):
    """Clip a set of gradients by their global L2 norm.

    Args:
        grads: list of 1-D float64 tensors. num_params flattened gradients;
            their lengths differ.
        maxNorm: float. Maximum allowed global norm.

    Returns:
        A list [clippedGrads, globalNorm] (a tuple works too):
            clippedGrads: list of float64 tensors. The clipped gradients, in
                order.
            globalNorm: 0-dim float64 tensor. Global norm measured before
                clipping.
    """
    pass
