def numRabbits(answers):
    from collections import Counter
    total = 0
    for x, c in Counter(answers).items():
        group = x + 1
        groups = (c + group - 1) // group
        total += groups * group
    return total
