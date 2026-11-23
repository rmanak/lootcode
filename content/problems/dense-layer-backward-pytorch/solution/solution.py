import torch


def denseBackward(X, W, b, dY, activation):
    # Forward with the library activations, backward by autograd: independent of
    # the numpy version's hand-written derivatives (relu'(0) = 0 in both).
    X, W, b = (t.detach().clone().requires_grad_(True) for t in (X, W, b))
    Z = X @ W + b
    act = {"linear": lambda z: z, "relu": torch.relu, "tanh": torch.tanh,
           "sigmoid": torch.sigmoid}[activation]
    act(Z).backward(dY)
    return [X.grad, W.grad, b.grad]
