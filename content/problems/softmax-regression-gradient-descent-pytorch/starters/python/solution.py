import torch


def softmaxRegressionGD(X, y, numClasses, lr, steps):
    """X: (N, d) float64 tensor; y: (N,) int64 tensor of labels in
    [0, numClasses); numClasses, steps: int; lr: float.
    Return [W, b, lossHistory]: W (d, numClasses), b (numClasses,),
    lossHistory (steps,), all float64."""
    pass
