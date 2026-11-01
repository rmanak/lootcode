import json


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _has_type(v, t):
    if t == "null":
        return v is None
    if t == "boolean":
        return isinstance(v, bool)
    if t == "integer":                       # JSON Schema: 3.0 is an integer, true is not
        return _is_number(v) and (isinstance(v, int) or v.is_integer())
    if t == "number":
        return _is_number(v)
    if t == "string":
        return isinstance(v, str)
    if t == "array":
        return isinstance(v, list)
    return isinstance(v, dict)               # "object"


def _equal(a, b):
    """JSON equality: 1 equals 1.0, true never equals 1, object key order is irrelevant."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if _is_number(a) and _is_number(b):
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_equal(a[k], b[k]) for k in a)
    return type(a) is type(b) and a == b     # strings and null


def _check(schema, v, path, errors):
    if "type" in schema:
        types = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_has_type(v, t) for t in types):
            errors.append([path, "type"])
            return                           # nothing else is checked on a wrongly-typed value
    if "enum" in schema and not any(_equal(v, e) for e in schema["enum"]):
        errors.append([path, "enum"])
    if _is_number(v):
        if "minimum" in schema and v < schema["minimum"]:
            errors.append([path, "minimum"])
        if "exclusiveMinimum" in schema and v <= schema["exclusiveMinimum"]:
            errors.append([path, "exclusiveMinimum"])
        if "maximum" in schema and v > schema["maximum"]:
            errors.append([path, "maximum"])
        if "exclusiveMaximum" in schema and v >= schema["exclusiveMaximum"]:
            errors.append([path, "exclusiveMaximum"])
    elif isinstance(v, str):
        if "minLength" in schema and len(v) < schema["minLength"]:
            errors.append([path, "minLength"])
        if "maxLength" in schema and len(v) > schema["maxLength"]:
            errors.append([path, "maxLength"])
    elif isinstance(v, list):
        if "minItems" in schema and len(v) < schema["minItems"]:
            errors.append([path, "minItems"])
        if "maxItems" in schema and len(v) > schema["maxItems"]:
            errors.append([path, "maxItems"])
        if schema.get("uniqueItems") and any(_equal(v[i], v[j]) for i in range(len(v)) for j in range(i)):
            errors.append([path, "uniqueItems"])
        if "items" in schema:
            for i, item in enumerate(v):
                _check(schema["items"], item, f"{path}[{i}]", errors)
    elif isinstance(v, dict):
        props = schema.get("properties", {})
        for name in schema.get("required", []):
            if name not in v:
                errors.append([f"{path}.{name}", "required"])
        for name, sub in props.items():          # the schema's property order
            if name in v:
                _check(sub, v[name], f"{path}.{name}", errors)
        extra = schema.get("additionalProperties", True)
        for name, value in v.items():            # the arguments' key order
            if name in props:
                continue
            if extra is False:
                errors.append([f"{path}.{name}", "additionalProperties"])
            elif isinstance(extra, dict):
                _check(extra, value, f"{path}.{name}", errors)


def validateToolCalls(tools, calls):
    schemas = {tool["name"]: tool["parameters"] for tool in tools}
    out = []
    for call in calls:
        if call["name"] not in schemas:
            out.append([["$", "unknownTool"]])
            continue
        try:
            args = json.loads(call["arguments"])
        except ValueError:                       # JSONDecodeError, including "" and trailing data
            out.append([["$", "invalidJson"]])
            continue
        errors = []
        _check(schemas[call["name"]], args, "$", errors)
        out.append(errors)
    return out
