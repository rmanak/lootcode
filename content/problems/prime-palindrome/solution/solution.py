def primePalindrome(N):
    def is_prime(x):
        if x < 2:
            return False
        if x % 2 == 0:
            return x == 2
        i = 3
        while i * i <= x:
            if x % i == 0:
                return False
            i += 2
        return True
    if 8 <= N <= 11:
        return 11
    length = len(str(N))
    while True:
        if length % 2 == 0:
            length += 1
            continue
        half = length // 2 + 1
        for first in range(10 ** (half - 1), 10 ** half):
            s = str(first)
            pal = int(s + s[-2::-1])
            if pal >= N and is_prime(pal):
                return pal
        length += 1
