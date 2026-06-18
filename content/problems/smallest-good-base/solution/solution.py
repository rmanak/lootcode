def smallestGoodBase(n):
    num = int(n)
    for length in range(num.bit_length(), 1, -1):
        # length = number of all-ones digits; find base k via binary search
        lo, hi = 2, int(num ** (1.0 / (length - 1))) + 2
        while lo <= hi:
            mid = (lo + hi) // 2
            s, cur, over = 0, 1, False
            for _ in range(length):
                s += cur
                if s > num:
                    over = True
                    break
                cur *= mid
            if not over and s == num:
                return str(mid)
            if over or s > num:
                hi = mid - 1
            else:
                lo = mid + 1
    return str(num - 1)
