def numTilePossibilities(tiles):
    from collections import Counter
    cnt = Counter(tiles)

    def dfs(counter):
        total = 0
        for ch in counter:
            if counter[ch] > 0:
                counter[ch] -= 1
                total += 1 + dfs(counter)
                counter[ch] += 1
        return total

    return dfs(cnt)
