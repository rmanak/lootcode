import math


def grpoLoss(rewards, newLogps, oldLogps, refLogps, clipEps, beta, aggregation):
    g = len(rewards[0])
    advantages = []
    for group in rewards:
        mean = math.fsum(group) / g
        std = math.sqrt(math.fsum((r - mean) ** 2 for r in group) / (g - 1))   # sample std, like torch.std
        advantages.append([(r - mean) / (std + 1e-4) for r in group])
    flat_adv = [a for row in advantages for a in row]   # completion k belongs to group k // G

    seq_loss, seq_kl, tok_loss, tok_kl = [], [], [], []
    clipped = total = 0
    for a, new, old, ref in zip(flat_adv, newLogps, oldLogps, refLogps):
        losses, kls = [], []
        for ln, lo, lr in zip(new, old, ref):
            ratio = math.exp(ln - lo)
            clipped_ratio = min(max(ratio, 1 - clipEps), 1 + clipEps)
            surrogate = min(ratio * a, clipped_ratio * a)       # pessimistic bound
            kl = math.exp(lr - ln) - (lr - ln) - 1              # k3 estimator, always >= 0
            losses.append(-(surrogate - beta * kl))
            kls.append(kl)
            if (ratio > 1 + clipEps and a > 0) or (ratio < 1 - clipEps and a < 0):
                clipped += 1
            total += 1
        seq_loss.append(math.fsum(losses) / len(losses))
        seq_kl.append(math.fsum(kls) / len(kls))
        tok_loss += losses
        tok_kl += kls
    if aggregation == "sequence":       # average within each completion, then over completions
        loss, kl = math.fsum(seq_loss) / len(seq_loss), math.fsum(seq_kl) / len(seq_kl)
    else:                               # "token": every token counts equally
        loss, kl = math.fsum(tok_loss) / len(tok_loss), math.fsum(tok_kl) / len(tok_kl)
    return [advantages, loss, clipped / total, kl]
