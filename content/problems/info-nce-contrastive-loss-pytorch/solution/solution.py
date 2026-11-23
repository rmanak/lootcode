import torch
import torch.nn.functional as F


def infoNCE(U, V, temperature):
    # The reference uses autograd (the solver may not): it is an implementation
    # independent of the numpy version's hand-derived gradient, so the two
    # agreeing is a real check (scripts/sync_twin_tests.py check).
    U = U.detach().clone().requires_grad_(True)
    V = V.detach().clone().requires_grad_(True)
    S = F.normalize(U, dim=1) @ F.normalize(V, dim=1).T / temperature
    target = torch.arange(S.shape[0])
    loss = (F.cross_entropy(S, target) + F.cross_entropy(S.T, target)) / 2
    loss.backward()
    return [loss.detach(), U.grad, V.grad]
