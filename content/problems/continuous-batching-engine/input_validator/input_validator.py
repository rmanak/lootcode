"""Input-constraint validator for problem 'continuous-batching-engine'.

Hand-written. requests: 1..500 entries, each [prompt, maxTokens] with a
prompt of 1..50 ints in [0, vocabSize) and maxTokens an int in [1, 200];
batchSize an int in [1, 64]; vocabSize an int in [2, 1000]; stopToken an
int in [0, vocabSize); continuous a bool.
"""


def _int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def validate_input(requests, batchSize, stopToken, vocabSize, continuous):
    if not (_int(vocabSize) and 2 <= vocabSize <= 1000):
        return False
    if not (_int(stopToken) and 0 <= stopToken < vocabSize):
        return False
    if not (_int(batchSize) and 1 <= batchSize <= 64) or not isinstance(continuous, bool):
        return False
    if not isinstance(requests, list) or not 1 <= len(requests) <= 500:
        return False
    for r in requests:
        if not isinstance(r, list) or len(r) != 2:
            return False
        prompt, mx = r
        if not isinstance(prompt, list) or not 1 <= len(prompt) <= 50:
            return False
        if not all(_int(t) and 0 <= t < vocabSize for t in prompt):
            return False
        if not (_int(mx) and 1 <= mx <= 200):
            return False
    return True
