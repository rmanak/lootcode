import numpy as np


def batchNormTrain(x, gamma, beta, dy, eps, runningMean, runningVar, momentum):
    """Batch norm in training mode: forward, backward and running-stat update.

    Args:
        x: list of lists of floats, shape (batch_size, num_features). Input
            batch.
        gamma: list of floats, shape (num_features,). Scale.
        beta: list of floats, shape (num_features,). Shift.
        dy: list of lists of floats, shape (batch_size, num_features). Upstream
            gradient dLoss/dy.
        eps: float. Added to the variance for stability.
        runningMean: list of floats, shape (num_features,). Running mean before
            this step.
        runningVar: list of floats, shape (num_features,). Running variance
            before this step.
        momentum: float. Running-stat update momentum.

    Returns:
        A list [y, dx, dgamma, dbeta, newRunningMean, newRunningVar] (a tuple
        works too):
            y: np.ndarray of floats. Normalized output.
            dx: np.ndarray of floats. Gradient w.r.t. x.
            dgamma: np.ndarray of floats. Gradient w.r.t. gamma.
            dbeta: np.ndarray of floats. Gradient w.r.t. beta.
            newRunningMean: np.ndarray of floats. Updated running mean.
            newRunningVar: np.ndarray of floats. Updated running variance.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
