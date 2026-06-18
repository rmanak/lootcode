def maxSatisfaction(satisfaction):
    satisfaction.sort(reverse=True)
    total = 0
    run = 0
    for x in satisfaction:
        run += x
        if run <= 0:
            break
        total += run
    return total
