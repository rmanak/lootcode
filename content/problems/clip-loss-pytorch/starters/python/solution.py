import torch
import torch.nn.functional as F


def clip_loss(image_feat: torch.Tensor, text_feat: torch.Tensor,
              temperature: float) -> torch.Tensor:
    """image_feat, text_feat: (N, D) float32, un-normalized; row i of each is a pair.
    Return the symmetric CLIP loss as a 0-dim float32 tensor."""
    pass
