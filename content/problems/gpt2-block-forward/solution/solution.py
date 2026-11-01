import math

import numpy as np


def _layer_norm(x, gamma, beta, eps=1e-5):
    mu = x.mean(axis=1, keepdims=True)
    var = ((x - mu) ** 2).mean(axis=1, keepdims=True)       # biased variance
    return (x - mu) / np.sqrt(var + eps) * gamma + beta


def _gelu_tanh(x):                                          # GPT-2's "gelu_new"
    return 0.5 * x * (1.0 + np.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * x ** 3)))


def gpt2Block(x, params, numHeads):
    P = {k: np.asarray(v, dtype=float) for k, v in params.items()}
    x = np.asarray(x, dtype=float)                          # (T, d)
    T, d = x.shape
    dh = d // numHeads

    # Attention sub-block: pre-LayerNorm, fused QKV projection, causal heads, residual.
    h = _layer_norm(x, P["ln1Gamma"], P["ln1Beta"])
    qkv = h @ P["attnW"] + P["attnB"]                       # (T, 3d) laid out as [q | k | v]
    q, k, v = qkv[:, :d], qkv[:, d:2 * d], qkv[:, 2 * d:]
    causal = np.tril(np.ones((T, T), dtype=bool))
    heads = []
    for i in range(numHeads):
        c = slice(i * dh, (i + 1) * dh)
        s = np.where(causal, q[:, c] @ k[:, c].T / math.sqrt(dh), -np.inf)
        w = np.exp(s - s.max(axis=1, keepdims=True))
        w /= w.sum(axis=1, keepdims=True)
        heads.append(w @ v[:, c])
    x = x + (np.concatenate(heads, axis=1) @ P["attnProjW"] + P["attnProjB"])

    # MLP sub-block: pre-LayerNorm, d -> 4d -> d, residual.
    h = _layer_norm(x, P["ln2Gamma"], P["ln2Beta"])
    x = x + (_gelu_tanh(h @ P["fcW"] + P["fcB"]) @ P["projW"] + P["projB"])
    return x.tolist()
