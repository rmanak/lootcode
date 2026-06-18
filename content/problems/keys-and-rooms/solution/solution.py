def canVisitAllRooms(rooms):
    seen = {0}
    stack = [0]
    while stack:
        r = stack.pop()
        for k in rooms[r]:
            if k not in seen:
                seen.add(k)
                stack.append(k)
    return len(seen) == len(rooms)
