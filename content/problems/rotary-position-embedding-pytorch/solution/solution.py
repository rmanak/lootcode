import torch


def applyRope(x, positions, base, style):
    T, d = x.shape
    half = d // 2
    theta = base ** (-2.0 * torch.arange(half, dtype=x.dtype) / d)  # one frequency per pair
    ang = positions.to(x.dtype)[:, None] * theta                      # (T, d/2)
    cos, sin = ang.cos(), ang.sin()
    if style == "interleaved":
        pairs = x.view(T, half, 2)                                    # pairs (0,1), (2,3), ...
        a, b = pairs[..., 0], pairs[..., 1]
        return torch.stack((a * cos - b * sin, a * sin + b * cos), dim=-1).reshape(T, d)
    a, b = x[:, :half], x[:, half:]                                   # pairs (i, i + d/2)
    return torch.cat((a * cos - b * sin, a * sin + b * cos), dim=-1)
