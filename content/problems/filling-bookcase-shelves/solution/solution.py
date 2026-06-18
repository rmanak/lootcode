def minHeightShelves(books, shelfWidth):
    n = len(books)
    INF = float('inf')
    dp = [0] + [INF] * n
    for i in range(1, n + 1):
        width = 0
        height = 0
        j = i
        while j >= 1 and width + books[j - 1][0] <= shelfWidth:
            width += books[j - 1][0]
            height = max(height, books[j - 1][1])
            dp[i] = min(dp[i], dp[j - 1] + height)
            j -= 1
    return dp[n]
