import numpy as np


def softmaxRegressionGD(X, y, numClasses, lr, steps):
    """Fit multinomial (softmax) regression with full-batch gradient descent.

    Args:
        X: list of lists of floats, shape (num_samples, num_features). One
            sample per row.
        y: list of ints, shape (num_samples,). Labels in [0, numClasses).
        numClasses: int. Number of classes.
        lr: float. Learning rate.
        steps: int. Number of gradient-descent steps.

    Returns:
        A list [W, b, lossHistory] (a tuple works too):
            W: np.ndarray of floats. Learned weights.
            b: np.ndarray of floats. Learned biases.
            lossHistory: np.ndarray of floats. Loss recorded at every step.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
