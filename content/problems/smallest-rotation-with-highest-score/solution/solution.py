def bestRotation(nums):
    n = len(nums)
    best_k, best = 0, -1
    for K in range(n):
        score = 0
        for i in range(n):
            if nums[(K + i) % n] <= i:
                score += 1
        if score > best:
            best, best_k = score, K
    return best_k
