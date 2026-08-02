class KeyValueStore:
    def __init__(self):
        self.store = {}
        self.snaps = []

    def set(self, key, value):
        self.store[key] = value

    def get(self, key):
        return self.store.get(key)

    def delete(self, key):
        self.store.pop(key, None)

    def snapshot(self):
        self.snaps.append(dict(self.store))
        return len(self.snaps) - 1

    def getAt(self, key, id):
        if 0 <= id < len(self.snaps):
            return self.snaps[id].get(key)
        return None
