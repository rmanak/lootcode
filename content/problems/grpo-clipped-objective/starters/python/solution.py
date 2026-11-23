import math


def grpoLoss(rewards, newLogps, oldLogps, refLogps, clipEps, beta, aggregation):
    """GRPO: group-normalized advantages and the clipped policy objective.

    Args:
        rewards: list of lists of floats, shape (num_prompts, group_size). One
            reward per completion.
        newLogps: list of lists of floats. num_prompts * group_size per-token
            log-probs under the current policy; completion k has its own length
            num_tokens_k.
        oldLogps: list of lists of floats. Same layout, under the sampling
            policy.
        refLogps: list of lists of floats. Same layout, under the reference
            policy.
        clipEps: float. PPO clip range.
        beta: float. KL-penalty weight.
        aggregation: str. "sequence" or "token".

    Returns:
        A list [advantages, loss, clipFraction, meanKl] (a tuple works too):
            advantages: np.ndarray of floats. Group-normalized advantages.
            loss: float. The objective to minimize.
            clipFraction: float. Fraction of tokens clipped.
            meanKl: float. Mean KL estimate to the reference.

    A plain (nested) Python list is accepted wherever an np.ndarray is.
    """
    pass
