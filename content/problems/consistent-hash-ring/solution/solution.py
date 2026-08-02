import bisect


class HashRing:
    def __init__(self):
        self.servers = []

    def addServer(self, id):
        i = bisect.bisect_left(self.servers, id)
        if i == len(self.servers) or self.servers[i] != id:
            self.servers.insert(i, id)

    def removeServer(self, id):
        i = bisect.bisect_left(self.servers, id)
        if i < len(self.servers) and self.servers[i] == id:
            self.servers.pop(i)

    def getServer(self, key):
        if not self.servers:
            return None
        i = bisect.bisect_left(self.servers, key)
        return self.servers[i] if i < len(self.servers) else self.servers[0]
