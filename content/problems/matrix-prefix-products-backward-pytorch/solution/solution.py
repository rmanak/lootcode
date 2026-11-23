import torch


def prefixProductsBackward(W, dP):
    Wg = W.detach().requires_grad_(True)
    acc = torch.eye(W.shape[1], dtype=W.dtype)
    prefixes = []
    for i in range(W.shape[0]):
        acc = acc @ Wg[i]
        prefixes.append(acc)
    P = torch.stack(prefixes)
    (dW,) = torch.autograd.grad((dP * P).sum(), (Wg,))     # L = sum_i <dP_i, P_i>
    return [P.detach(), dW]
