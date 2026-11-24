import torch


def softmaxRegressionGD(X, y, numClasses, lr, steps):
    """Fit multinomial (softmax) regression with full-batch gradient descent.

    Args:
        X: float32 tensor, shape (num_samples, num_features). One sample per
            row.
        y: int64 tensor, shape (num_samples,). Labels in [0, numClasses).
        numClasses: int. Number of classes.
        lr: float. Learning rate.
        steps: int. Number of gradient-descent steps.

    Returns:
        A list [W, b, lossHistory] (a tuple works too):
            W: float32 tensor. Learned weights.
            b: float32 tensor. Learned biases.
            lossHistory: float32 tensor. Loss recorded at every step.
    """
    pass
