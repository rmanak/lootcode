def minTravelCost(target, capacity, position, price):
    """Cheapest way to drive `target` units starting on a full tank.

    At every station the choice is forced once you know where the next
    strictly cheaper station is: if it is within one tank, buy only enough
    fuel to coast to it; otherwise this is the cheapest fuel in range, so
    fill the tank right up. A monotonic stack finds all those "next cheaper"
    stations in one pass, making the whole thing O(m).
    """
    m = len(position)
    stops = position + [target]

    # Any leg longer than a full tank strands the car, including A -> first stop.
    if position[0] > capacity:
        return -1
    for i in range(m):
        if stops[i + 1] - stops[i] > capacity:
            return -1

    # next_cheaper[i] = leftmost j > i with price[j] < price[i]  (m if none).
    next_cheaper = [m] * m
    stack = []
    for i in range(m):
        while stack and price[stack[-1]] > price[i]:
            next_cheaper[stack.pop()] = i
        stack.append(i)

    fuel = capacity - position[0]          # fuel left on arrival at station 0
    total = 0
    for i in range(m):
        remaining = target - position[i]
        if fuel >= remaining:              # already able to coast to B
            return total
        j = next_cheaper[i]
        reach = (position[j] - position[i]) if j < m else remaining
        need = reach if reach < capacity else capacity
        if fuel < need:
            total += (need - fuel) * price[i]
            fuel = need
        if fuel >= remaining:
            return total
        fuel -= stops[i + 1] - position[i]
    return -1
