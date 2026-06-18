def sumFourDivisors(nums):
    def four_sum(x):
        divs = []
        i = 1
        while i * i <= x:
            if x % i == 0:
                divs.append(i)
                if i != x // i:
                    divs.append(x // i)
                if len(divs) > 4:
                    return 0
            i += 1
        return sum(divs) if len(divs) == 4 else 0
    return sum(four_sum(x) for x in nums)
