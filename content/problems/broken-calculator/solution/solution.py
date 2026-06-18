def brokenCalc(startValue, target):
    ops = 0
    while target > startValue:
        if target % 2 == 0:
            target //= 2
        else:
            target += 1
        ops += 1
    return ops + (startValue - target)
