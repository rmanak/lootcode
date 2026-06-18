def numBusesToDestination(routes, source, target):
    from collections import defaultdict, deque
    if source == target:
        return 0
    stop_buses = defaultdict(list)
    for bus, route in enumerate(routes):
        for s in route:
            stop_buses[s].append(bus)
    visited_bus = set()
    visited_stop = {source}
    q = deque([(source, 0)])
    while q:
        stop, d = q.popleft()
        for bus in stop_buses[stop]:
            if bus in visited_bus:
                continue
            visited_bus.add(bus)
            for ns in routes[bus]:
                if ns == target:
                    return d + 1
                if ns not in visited_stop:
                    visited_stop.add(ns)
                    q.append((ns, d + 1))
    return -1
