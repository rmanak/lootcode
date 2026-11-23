import torch


def classifierFreeGuidance(noisePred, guidanceScale, guidanceRescale):
    uncond, cond = noisePred.chunk(2)
    guided = torch.lerp(uncond, cond, guidanceScale)
    if guidanceRescale > 0:
        ratio = cond.std(dim=1, keepdim=True) / guided.std(dim=1, keepdim=True)
        guided = torch.lerp(guided, guided * ratio, guidanceRescale)
    return guided
