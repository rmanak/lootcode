from collections import defaultdict


class SparseMatrix:
    def __init__(self, rows, cols, entries):
        self.by_row = defaultdict(dict)    # i -> {j: value}
        self.by_col = defaultdict(dict)    # j -> {i: value}
        for i, j, v in entries:
            self.set(i, j, v)

    def set(self, i, j, value):
        if value:
            self.by_row[i][j] = value
            self.by_col[j][i] = value
        else:
            self.by_row[i].pop(j, None)
            self.by_col[j].pop(i, None)

    @staticmethod
    def _product(vector, index):
        out = defaultdict(int)
        for k, x in vector:
            for t, m in index.get(k, {}).items():
                out[t] += m * x
        return [[t, s] for t, s in sorted(out.items()) if s]

    def multiplyVector(self, vector):
        return self._product(vector, self.by_col)    # (Mv)_i = sum_j M[i][j] v_j

    def vectorMultiply(self, vector):
        return self._product(vector, self.by_row)    # (v^T M)_j = sum_i v_i M[i][j]
