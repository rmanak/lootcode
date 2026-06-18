def kthGrammar(N, K):
    return bin(K - 1).count("1") & 1
