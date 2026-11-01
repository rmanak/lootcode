import math


def preprocess(train, test, columnTypes):
    encoders = []
    for j, kind in enumerate(columnTypes):
        seen = [row[j] for row in train if row[j] is not None]
        if kind == "numeric":
            mean = math.fsum(seen) / len(seen)
            if all(v == seen[0] for v in seen):
                encoders.append(("const", None))            # constant column: always 0
            else:
                std = math.sqrt(math.fsum((v - mean) ** 2 for v in seen) / len(seen))
                encoders.append(("num", (mean, std)))
        else:
            encoders.append(("cat", sorted(set(seen))))

    def transform(rows):
        out = []
        for row in rows:
            feats = []
            for j, (kind, info) in enumerate(encoders):
                v = row[j]
                if kind == "const":
                    feats.append(0.0)
                elif kind == "num":
                    mean, std = info
                    feats.append(0.0 if v is None else (v - mean) / std)   # missing -> the mean -> 0
                else:
                    feats.extend(1.0 if v == c else 0.0 for c in info)    # unseen / missing -> zeros
            out.append(feats)
        return out

    return [transform(train), transform(test)]
