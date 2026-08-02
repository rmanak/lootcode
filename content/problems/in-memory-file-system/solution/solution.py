class FileSystem:
    def __init__(self):
        self.root = {"dirs": {}, "files": {}}

    def _dir(self, parts, create=False):
        node = self.root
        for p in parts:
            if p not in node["dirs"]:
                if not create:
                    return None
                node["dirs"][p] = {"dirs": {}, "files": {}}
            node = node["dirs"][p]
        return node

    @staticmethod
    def _parts(path):
        return [p for p in path.split("/") if p]

    def ls(self, path):
        parts = self._parts(path)
        if parts:
            parent = self._dir(parts[:-1])
            if parent and parts[-1] in parent["files"]:
                return [parts[-1]]
        node = self._dir(parts)
        return sorted(list(node["dirs"].keys()) + list(node["files"].keys()))

    def mkdir(self, path):
        self._dir(self._parts(path), create=True)

    def addContentToFile(self, filePath, content):
        parts = self._parts(filePath)
        node = self._dir(parts[:-1], create=True)
        node["files"][parts[-1]] = node["files"].get(parts[-1], "") + content

    def readContentFromFile(self, filePath):
        parts = self._parts(filePath)
        return self._dir(parts[:-1])["files"][parts[-1]]
