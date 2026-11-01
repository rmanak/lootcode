"""Input-constraint validator for problem 'validate-tool-call-arguments'.

Hand-written. `validate_input(...)` returns True iff its arguments satisfy the
input constraints stated in the problem. Before adding a new (input, expected)
test case, run it over the candidate input to confirm the input is in-range.
See docs/input-validators.md.

Checks every stated bound:
- 1..20 tools, each {"name", "parameters"} with a unique non-empty name;
- every schema uses only the listed keywords with the stated value types,
  nests at most 6 schemas deep, names properties and required entries with
  identifiers ([A-Za-z_][A-Za-z0-9_]*, at most 20 chars), and has no
  NaN/Infinity in enum or the numeric bounds;
- 1..50 calls, each {"name", "arguments"} with string values, arguments at
  most 2000 characters;
- when arguments parses as JSON: no NaN/Infinity/-Infinity tokens, no
  repeated key in any object, every key an identifier, nesting at most 20.
"""
import json
import math
import re

_ID = re.compile(r"[A-Za-z_][A-Za-z0-9_]{0,19}\Z")
_TYPES = {"null", "boolean", "integer", "number", "string", "array", "object"}
_NUM_KEYS = ("minimum", "exclusiveMinimum", "maximum", "exclusiveMaximum")
_LEN_KEYS = ("minLength", "maxLength", "minItems", "maxItems")
_ALLOWED = {"type", "enum", "items", "properties", "required", "additionalProperties", "uniqueItems",
            *_NUM_KEYS, *_LEN_KEYS}


def _finite_json(v, depth=0):
    if depth > 20:
        return False
    if isinstance(v, bool) or v is None or isinstance(v, str):
        return True
    if isinstance(v, (int, float)):
        return math.isfinite(v)
    if isinstance(v, list):
        return all(_finite_json(x, depth + 1) for x in v)
    if isinstance(v, dict):
        return all(isinstance(k, str) and _finite_json(x, depth + 1) for k, x in v.items())
    return False


def _schema_ok(s, depth=1):
    if depth > 6 or not isinstance(s, dict) or not set(s) <= _ALLOWED:
        return False
    if "type" in s:
        t = s["type"]
        ts = t if isinstance(t, list) else [t]
        if not ts or len(set(map(str, ts))) != len(ts) or not all(isinstance(x, str) and x in _TYPES for x in ts):
            return False
    if "enum" in s and not (isinstance(s["enum"], list) and s["enum"] and _finite_json(s["enum"])):
        return False
    for k in _NUM_KEYS:
        if k in s and not (isinstance(s[k], (int, float)) and not isinstance(s[k], bool) and math.isfinite(s[k])):
            return False
    for k in _LEN_KEYS:
        if k in s and not (isinstance(s[k], int) and not isinstance(s[k], bool) and 0 <= s[k] <= 1000):
            return False
    if "uniqueItems" in s and not isinstance(s["uniqueItems"], bool):
        return False
    if "items" in s and not _schema_ok(s["items"], depth + 1):
        return False
    if "properties" in s:
        p = s["properties"]
        if not isinstance(p, dict) or not all(_ID.match(k) and _schema_ok(v, depth + 1) for k, v in p.items()):
            return False
    if "required" in s:
        r = s["required"]
        if not (isinstance(r, list) and all(isinstance(x, str) and _ID.match(x) for x in r) and len(set(r)) == len(r)):
            return False
    if "additionalProperties" in s:
        a = s["additionalProperties"]
        if not (isinstance(a, bool) or _schema_ok(a, depth + 1)):
            return False
    return True


def _no_dupes(pairs):
    keys = [k for k, _ in pairs]
    if len(set(keys)) != len(keys) or not all(_ID.match(k) for k in keys):
        raise ValueError("bad keys")
    return dict(pairs)


def _bad_constant(name):
    raise ValueError(name)


def _args_ok(text):
    if not isinstance(text, str) or len(text) > 2000:
        return False
    try:
        json.loads(text)
    except (ValueError, RecursionError):
        return True                          # malformed JSON is a legal input (it is the point)
    try:
        v = json.loads(text, object_pairs_hook=_no_dupes, parse_constant=_bad_constant)
    except (ValueError, RecursionError):
        return False                         # parses only thanks to NaN/Infinity, a repeated key or a bad key
    return _finite_json(v)


def validate_input(tools, calls):
    if not isinstance(tools, list) or not 1 <= len(tools) <= 20:
        return False
    names = []
    for t in tools:
        if not (isinstance(t, dict) and set(t) == {"name", "parameters"} and isinstance(t["name"], str)
                and t["name"] and _schema_ok(t["parameters"])):
            return False
        names.append(t["name"])
    if len(set(names)) != len(names):
        return False
    if not isinstance(calls, list) or not 1 <= len(calls) <= 50:
        return False
    return all(isinstance(c, dict) and set(c) == {"name", "arguments"} and isinstance(c["name"], str)
               and _args_ok(c["arguments"]) for c in calls)
