import math


def clipGradients(grads, maxNorm):
    """Clip a set of gradients by their global L2 norm.

    Args:
        grads: list of lists of floats. num_params flattened gradients; their
            lengths differ.
        maxNorm: float. Maximum allowed global norm.

    Returns:
        A list [clippedGrads, globalNorm] (a tuple works too):
            clippedGrads: list of np.ndarrays of floats. The clipped gradients,
                in order.
            globalNorm: float. Global norm measured before clipping.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
