def multiply(num1, num2):
    if num1 == "0" or num2 == "0":
        return "0"
    n, m = len(num1), len(num2)
    res = [0] * (n + m)
    for i in range(n - 1, -1, -1):
        for j in range(m - 1, -1, -1):
            mul = (ord(num1[i]) - 48) * (ord(num2[j]) - 48)
            p1, p2 = i + j, i + j + 1
            total = mul + res[p2]
            res[p2] = total % 10
            res[p1] += total // 10
    s = "".join(map(str, res)).lstrip("0")
    return s if s else "0"
