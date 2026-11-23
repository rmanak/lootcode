import torch
import torch.nn.functional as F


def scaledDotProductAttention(Q, K, V, mask):
    allowed = mask.bool()
    scores = Q @ K.T / Q.shape[1] ** 0.5
    weights = torch.softmax(scores.masked_fill(~allowed, float("-inf")), dim=-1)
    # The output through the library kernel, an independent path from `weights`.
    out = F.scaled_dot_product_attention(Q[None], K[None], V[None], attn_mask=allowed)[0]
    return [out, weights]
