# Validate Tool-Call Arguments Against a JSON Schema

An LLM agent calls tools by emitting a tool name and its arguments as a
**JSON string**. Before running anything, the agent runtime checks each call
against the tool's declared parameter schema and reports every problem, so the
model can repair its call. Implement that check for a subset of JSON Schema.

`tools` is a list of `{"name", "parameters"}`, where `parameters` is a
schema. `calls` is a list of `{"name", "arguments"}`, where `arguments` is a
string. For each call, in order, produce a list of errors `[path, code]`:

1. If no tool has that name: `[["$", "unknownTool"]]`. Nothing else is
   checked.
2. Parse `arguments` as **strict JSON** (Python's `json.loads`). The whole
   string must be one JSON value, optionally surrounded by whitespace. If that
   fails, including for an empty string: `[["$", "invalidJson"]]`.
3. Otherwise, validate the parsed value against the schema, starting at path
   `"$"`. A valid call yields `[]`.

**Paths.** The root is `"$"`. An object property `key` appends `.key`, and
an array element `i` appends `[i]`, as in `"$.to[1]"`.

**Validating a value `v` against a schema**, in this exact order. Every
keyword is optional.

1. `type`, a type name or a list of names (`v` must match at least one):
   `"null"`, `"boolean"`, `"string"`, `"array"`, `"object"`, `"number"` (any
   number, but **not** a boolean), and `"integer"` (a number with no fractional
   part, so `3.0` **is** an integer and `true` is not). On a mismatch, report
   `"type"` and **check nothing else** about `v` or its children.
2. `enum`: `v` must equal one of the listed values under **JSON equality**.
   Numbers compare by value (`1` equals `1.0`), a boolean only ever equals a
   boolean (`true` is **not** `1`), arrays compare element by element, and
   objects compare as key→value maps regardless of key order. Report
   `"enum"`.
3. If `v` is a number: `minimum` (`v < minimum` is an error),
   `exclusiveMinimum` (`v <= exclusiveMinimum`), `maximum` (`v > maximum`),
   `exclusiveMaximum` (`v >= exclusiveMaximum`), checked in that order, each
   reported under its own name.
4. If `v` is a string: `minLength`, then `maxLength`, counted in characters
   (code points).
5. If `v` is an array: `minItems`, then `maxItems`. Then, if `uniqueItems` is
   `true` and any two elements are JSON-equal, report `"uniqueItems"` once.
   Then validate each element against `items`, in index order.
6. If `v` is an object:
    - First, `required`: for each listed name, in the listed order, that `v`
      lacks, report `[path.name, "required"]`.
    - Next, `properties`: for each property in the **schema's order** that `v`
      has, validate its value against that property's schema.
    - Finally, keys of `v` not in `properties`, in the **order they appear in
      the arguments**. If `additionalProperties` is `false`, report
      `[path.key, "additionalProperties"]`. If it is a schema, validate the
      value against it. If it is `true` or absent, accept the key.

Keywords that don't apply to `v`'s kind are ignored. For example, `minimum` on
a string does nothing.

**Return** one error list per call, in order.

## Constraints

- `1 <= len(tools) <= 20`, with unique, non-empty names.
  `1 <= len(calls) <= 50`
- Schemas use only the keywords above and nest at most 6 levels deep.
  Property names are identifiers (`[A-Za-z_][A-Za-z0-9_]*`, at most 20
  characters). Bounds are finite numbers. Lengths and item counts are
  integers in `[0, 1000]`
- Each `arguments` is at most 2000 characters. When it is valid JSON, it
  contains no `NaN` or `Infinity`, never repeats a key within one object, uses
  identifier keys only, and nests at most 20 deep

## Examples

**Example 1**
```
Input:  tools = [{"name": "get_weather", "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "minLength": 1},
                           "unit": {"enum": ["celsius", "fahrenheit"]},
                           "days": {"type": "integer", "minimum": 1, "maximum": 7}},
            "required": ["city"], "additionalProperties": false}}]
        calls = [{"name": "get_weather", "arguments": "{\"city\": \"Paris\", \"days\": 3.0}"},
                 {"name": "get_weather", "arguments": "{\"unit\": \"kelvin\", \"days\": true, \"country\": \"FR\", \"area\": 5}"},
                 {"name": "get_weather", "arguments": "{'city': 'Paris'}"},
                 {"name": "get_forecast", "arguments": "{city: Paris}"}]
Output: [[],
         [["$.city", "required"], ["$.unit", "enum"], ["$.days", "type"],
          ["$.country", "additionalProperties"], ["$.area", "additionalProperties"]],
         [["$", "invalidJson"]],
         [["$", "unknownTool"]]]
Explanation: 3.0 is an integer. true is not a number. The extra keys are
reported in the order the model wrote them, not sorted. Single quotes are not
JSON. The last call names a tool that doesn't exist, so its broken
arguments are never looked at.
```

**Example 2**
```
Input:  tools = [get_weather (as above), {"name": "send_email", "parameters": {
            "type": "object",
            "properties": {"to": {"type": "array", "items": {"type": "string", "minLength": 3},
                                  "minItems": 1, "uniqueItems": true},
                           "priority": {"type": ["integer", "null"], "exclusiveMinimum": 0}},
            "required": ["to", "subject"]}}]
        calls = [{"name": "send_email", "arguments": "{\"to\": [\"bob@x.io\", \"al\", \"bob@x.io\"], \"priority\": 0}"},
                 {"name": "send_email", "arguments": "{\"to\": [], \"subject\": \"hi\", \"priority\": null}"},
                 {"name": "send_email", "arguments": "[1, 2]"}]
Output: [[["$.subject", "required"], ["$.to", "uniqueItems"], ["$.to[1]", "minLength"],
          ["$.priority", "exclusiveMinimum"]],
         [["$.to", "minItems"]],
         [["$", "type"]]]
Explanation: the missing required key comes first. Then come the properties in
schema order: the array-level check on "to" before its elements, and then
"priority" (0 is not > 0). null matches the type list, and exclusiveMinimum
ignores non-numbers.
```

**Example 3**
```
Input:  tools = [{"name": "set_flag", "parameters": {
            "type": "object",
            "properties": {"value": {"enum": [1, "on"]}, "level": {"type": "integer", "minimum": 5}},
            "additionalProperties": {"type": "string"}}}]
        calls = [{"name": "set_flag", "arguments": "{\"value\": true, \"level\": 2.5, \"note\": 3}"},
                 {"name": "set_flag", "arguments": "{\"value\": 1.0, \"level\": 7, \"note\": \"ok\"}"},
                 {"name": "set_flag", "arguments": ""}]
Output: [[["$.value", "enum"], ["$.level", "type"], ["$.note", "type"]],
         [],
         [["$", "invalidJson"]]]
Explanation: true is not 1, but 1.0 is. 2.5 fails the type, so its minimum
is never checked. The extra key "note" must match the additionalProperties
schema. An empty string is not JSON.
```
