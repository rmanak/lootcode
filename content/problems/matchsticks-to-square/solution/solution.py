def makesquare(matchsticks):
    total = sum(matchsticks)
    if not matchsticks or total % 4 != 0:
        return False
    side = total // 4
    matchsticks.sort(reverse=True)
    if matchsticks[0] > side:
        return False
    sides = [0] * 4

    def dfs(i):
        if i == len(matchsticks):
            return True
        for j in range(4):
            if sides[j] + matchsticks[i] <= side:
                sides[j] += matchsticks[i]
                if dfs(i + 1):
                    return True
                sides[j] -= matchsticks[i]
            if sides[j] == 0:
                break
        return False

    return dfs(0)
