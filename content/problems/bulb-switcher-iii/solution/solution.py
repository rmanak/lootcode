def numTimesAllBlue(light):
    rightmost = 0
    ans = 0
    for i, b in enumerate(light):
        rightmost = max(rightmost, b)
        if rightmost == i + 1:
            ans += 1
    return ans
