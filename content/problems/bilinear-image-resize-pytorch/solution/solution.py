import torch
import torch.nn.functional as F


def resizeBilinear(image, outHeight, outWidth, alignCorners):
    out = F.interpolate(image[None, None], size=(outHeight, outWidth),
                        mode="bilinear", align_corners=alignCorners)
    return out[0, 0]
