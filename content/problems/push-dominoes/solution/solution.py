def pushDominoes(dominoes):
    n = len(dominoes)
    force = [0] * n
    f = 0
    for i in range(n):
        if dominoes[i] == 'R':
            f = n
        elif dominoes[i] == 'L':
            f = 0
        else:
            f = max(f - 1, 0)
        force[i] += f
    f = 0
    for i in range(n - 1, -1, -1):
        if dominoes[i] == 'L':
            f = n
        elif dominoes[i] == 'R':
            f = 0
        else:
            f = max(f - 1, 0)
        force[i] -= f
    return "".join('.' if x == 0 else ('R' if x > 0 else 'L') for x in force)
