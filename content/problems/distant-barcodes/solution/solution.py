def canRearrange(barcodes):
    from collections import Counter
    n = len(barcodes)
    if n == 0:
        return True
    return max(Counter(barcodes).values()) <= (n + 1) // 2
