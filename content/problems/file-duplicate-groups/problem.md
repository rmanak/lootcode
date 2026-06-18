Each entry in `files` is `[path, content]`. Return **the groups of paths whose
files have identical content**, including only groups with **two or more** paths.
Neither the order of the groups nor the order of paths within a group matters.

## Constraints
- `0 <= len(files) <= 2*10^4`; paths are unique.

## Examples
Input: `files = [["a","x"],["b","x"],["c","y"]]`
Output: `[["a","b"]]`

Input: `files = [["a","x"]]`
Output: `[]`

Input: `files = [["a","x"],["b","y"],["c","x"],["d","y"]]`
Output: `[["a","c"],["b","d"]]`
