import torch


def grpoLoss(rewards, newLogps, oldLogps, refLogps, clipEps, beta, aggregation):
    """GRPO: group-normalized advantages and the clipped policy objective.

    Args:
        rewards: float32 tensor, shape (num_prompts, group_size). One reward
            per completion.
        newLogps: list of 1-D float32 tensors. num_prompts * group_size
            per-token log-probs under the current policy; completion k has its
            own length num_tokens_k.
        oldLogps: list of 1-D float32 tensors. Same layout, under the sampling
            policy.
        refLogps: list of 1-D float32 tensors. Same layout, under the reference
            policy.
        clipEps: float. PPO clip range.
        beta: float. KL-penalty weight.
        aggregation: str. "sequence" or "token".

    Returns:
        A list [advantages, loss, clipFraction, meanKl] (a tuple works too):
            advantages: float32 tensor. Group-normalized advantages.
            loss: 0-dim float32 tensor. The objective to minimize.
            clipFraction: 0-dim float32 tensor. Fraction of tokens clipped.
            meanKl: 0-dim float32 tensor. Mean KL estimate to the reference.
    """
    pass
