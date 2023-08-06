def combinationSum(candidates,target):
    # does order of the subset matter what I mean is that if i can assume thr [2,2,3] is exactly same with [2,3,2]
    # index remain cur
    n = len(candidates)

    def dfs(index, remain, cur):
        if remain == 0:
            result.append(cur[:])
            return
        if remain < 0:
            return
        for i in range(index, n):
            # if i > index and nums[i] == nums[i - 1]
            dfs(i, remain - candidates[i], cur + [candidates[i]])
        return

    result = []
    dfs(0, target, [])
    return result