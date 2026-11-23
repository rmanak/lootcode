import torch


def batchNormTrain(x, gamma, beta, dy, eps, runningMean, runningVar, momentum):
    """x, dy: (N, D) float64 tensors; gamma, beta, runningMean, runningVar: (D,)
    float64 tensors; eps, momentum: float.
    Return [y, dx, dgamma, dbeta, newRunningMean, newRunningVar] as float64 tensors."""
    pass
