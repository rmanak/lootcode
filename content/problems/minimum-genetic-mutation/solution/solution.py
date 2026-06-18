def minMutation(startGene, endGene, bank):
    from collections import deque
    if startGene == endGene:
        return 0
    bankset = set(bank)
    if endGene not in bankset:
        return -1
    q = deque([(startGene, 0)])
    seen = {startGene}
    while q:
        gene, d = q.popleft()
        if gene == endGene:
            return d
        for i in range(len(gene)):
            for c in "ACGT":
                if c != gene[i]:
                    ng = gene[:i] + c + gene[i + 1:]
                    if ng in bankset and ng not in seen:
                        seen.add(ng)
                        q.append((ng, d + 1))
    return -1
