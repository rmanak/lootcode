def trap(height):
    if not height:
        return 0
    l, r = 0, len(height) - 1
    lm = rm = 0
    res = 0
    while l < r:
        if height[l] < height[r]:
            lm = max(lm, height[l])
            res += lm - height[l]
            l += 1
        else:
            rm = max(rm, height[r])
            res += rm - height[r]
            r -= 1
    return res
