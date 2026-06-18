A stream receives one character per query in `queries`. After appending each
character, return `true` if some word in `words` is a **suffix** of the stream so
far. Return one boolean per query.

## Constraints
- `1 <= len(words) <= 2000`, words are lowercase letters
- `1 <= len(queries) <= 4*10^4`, each query is a single lowercase letter

## Examples
Input: `words = ["cd","f","kl"], queries = ["a","b","c","d","f"]`
Output: `[false,false,false,true,true]`
Explanation: After `d` the suffix `cd` matches; after `f`, `f` matches.

Input: `words = ["ab"], queries = ["a","b"]`
Output: `[false,true]`
Explanation: After `b` the suffix `ab` matches.
