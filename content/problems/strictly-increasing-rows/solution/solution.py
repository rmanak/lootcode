def countIncreasingRows(matrix):
    count = 0
    for row in matrix:
        if all(row[i] < row[i + 1] for i in range(len(row) - 1)):
            count += 1
    return count
