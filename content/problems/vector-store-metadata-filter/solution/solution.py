import heapq

import numpy as np


class VectorStore:
    def __init__(self, dim):
        self.dim = dim
        self.records = {}                 # id -> (unit vector or None, metadata)

    def upsert(self, id, vector, metadata):
        v = np.asarray(vector, float)
        norm = np.linalg.norm(v)
        self.records[id] = (v / norm if norm > 0 else None, dict(metadata))

    def delete(self, id):
        self.records.pop(id, None)

    def query(self, vector, topK, filter):
        q = np.asarray(vector, float)
        qn = np.linalg.norm(q)
        ids, vecs, zero = [], [], []
        for rid, (u, meta) in self.records.items():
            if all(k in meta and meta[k] == val for k, val in filter.items()):
                if u is None or qn == 0:
                    zero.append(rid)
                else:
                    ids.append(rid)
                    vecs.append(u)
        scored = [(0.0, rid) for rid in zero]
        if ids:
            sims = np.stack(vecs) @ (q / qn)
            scored += list(zip(sims.tolist(), ids))
        best = heapq.nsmallest(topK, scored, key=lambda t: (-t[0], t[1]))
        return [[rid, score, self.records[rid][1]] for score, rid in best]

    def size(self):
        return len(self.records)
