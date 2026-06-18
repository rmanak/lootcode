def permute(nums):
    from itertools import permutations
    return [list(p) for p in permutations(nums)]
