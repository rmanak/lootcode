import math


def activations(x):
    """Numerically stable sigmoid, log-sigmoid and GELU, with derivatives.

    Args:
        x: list of floats, shape (num_values,). Input values.

    Returns:
        A list [sigmoid, sigmoidGrad, logSigmoid, gelu, geluGrad] (a tuple
        works too):
            sigmoid: np.ndarray of floats. sigmoid(x).
            sigmoidGrad: np.ndarray of floats. Its derivative.
            logSigmoid: np.ndarray of floats. log(sigmoid(x)).
            gelu: np.ndarray of floats. GELU(x).
            geluGrad: np.ndarray of floats. Its derivative.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
