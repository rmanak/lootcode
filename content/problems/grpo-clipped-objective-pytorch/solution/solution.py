import torch


def grpoLoss(rewards, newLogps, oldLogps, refLogps, clipEps, beta, aggregation):
    adv = (rewards - rewards.mean(dim=1, keepdim=True)) / (rewards.std(dim=1, keepdim=True) + 1e-4)
    lengths = torch.tensor([len(t) for t in newLogps])
    new, old, ref = torch.cat(newLogps), torch.cat(oldLogps), torch.cat(refLogps)
    a = adv.reshape(-1).repeat_interleave(lengths)        # each token gets its completion's A
    ratio = torch.exp(new - old)
    surrogate = torch.minimum(ratio * a, ratio.clamp(1 - clipEps, 1 + clipEps) * a)
    delta = ref - new
    kl = torch.exp(delta) - delta - 1
    token_loss = -(surrogate - beta * kl)
    clipped = ((ratio > 1 + clipEps) & (a > 0)) | ((ratio < 1 - clipEps) & (a < 0))
    if aggregation == "sequence":
        seq = torch.arange(len(lengths)).repeat_interleave(lengths)

        def per_completion(x):
            return torch.zeros(len(lengths), dtype=x.dtype).index_add_(0, seq, x) / lengths

        loss, mean_kl = per_completion(token_loss).mean(), per_completion(kl).mean()
    else:
        loss, mean_kl = token_loss.mean(), kl.mean()
    return [adv, loss, clipped.to(new.dtype).mean(), mean_kl]
