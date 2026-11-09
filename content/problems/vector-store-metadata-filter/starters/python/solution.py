import numpy as np


class VectorStore:
    def __init__(self, dim):
        pass

    def upsert(self, id, vector, metadata):
        pass

    def delete(self, id):
        pass

    def query(self, vector, topK, filter):
        pass

    def size(self):
        pass
