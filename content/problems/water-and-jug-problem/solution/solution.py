def canMeasureWater(x, y, z):
    from math import gcd
    if z == 0:
        return True
    if x + y < z:
        return False
    g = gcd(x, y)
    return g != 0 and z % g == 0
