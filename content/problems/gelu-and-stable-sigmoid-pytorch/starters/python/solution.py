import torch


def activations(x):
    """Numerically stable sigmoid, log-sigmoid and GELU, with derivatives.

    Args:
        x: float32 tensor, shape (num_values,). Input values.

    Returns:
        A list [sigmoid, sigmoidGrad, logSigmoid, gelu, geluGrad] (a tuple
        works too):
            sigmoid: float32 tensor. sigmoid(x).
            sigmoidGrad: float32 tensor. Its derivative.
            logSigmoid: float32 tensor. log(sigmoid(x)).
            gelu: float32 tensor. GELU(x).
            geluGrad: float32 tensor. Its derivative.
    """
    pass
