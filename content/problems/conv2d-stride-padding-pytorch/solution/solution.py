import torch
import torch.nn.functional as F


def conv2d(x, weight, bias, stride, padding):
    return F.conv2d(x[None], weight, bias, stride=stride, padding=padding)[0]
