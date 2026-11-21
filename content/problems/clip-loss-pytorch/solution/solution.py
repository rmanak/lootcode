import torch
import torch.nn.functional as F


def clip_loss(image_feat, text_feat, temperature):
    image = F.normalize(image_feat, dim=-1)
    text = F.normalize(text_feat, dim=-1)
    logits = image @ text.T / temperature
    targets = torch.arange(logits.shape[0])
    return (F.cross_entropy(logits, targets) + F.cross_entropy(logits.T, targets)) / 2
