def judgePoint24(cards):
    def solve(nums):
        if len(nums) == 1:
            return abs(nums[0] - 24) < 1e-6
        for i in range(len(nums)):
            for j in range(len(nums)):
                if i == j:
                    continue
                rest = [nums[k] for k in range(len(nums)) if k != i and k != j]
                cand = [nums[i] + nums[j], nums[i] - nums[j], nums[i] * nums[j]]
                if abs(nums[j]) > 1e-6:
                    cand.append(nums[i] / nums[j])
                for v in cand:
                    if solve(rest + [v]):
                        return True
        return False
    return solve([float(c) for c in cards])
