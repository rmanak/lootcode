def carFleet(target, position, speed):
    from fractions import Fraction
    cars = sorted(zip(position, speed), reverse=True)
    fleets = 0
    cur = Fraction(-1)
    for pos, spd in cars:
        t = Fraction(target - pos, spd)
        if t > cur:
            fleets += 1
            cur = t
    return fleets
