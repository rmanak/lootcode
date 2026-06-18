def countArrangement(N):
    count = [0]
    used = [False] * (N + 1)

    def dfs(pos):
        if pos > N:
            count[0] += 1
            return
        for num in range(1, N + 1):
            if not used[num] and (num % pos == 0 or pos % num == 0):
                used[num] = True
                dfs(pos + 1)
                used[num] = False

    dfs(1)
    return count[0]
