Replay `operations` against a trie and return **the list of results**. Operations
are `["insert", word]` → `null`; `["search", word]` → `true` if the exact word was
inserted; `["startsWith", prefix]` → `true` if any inserted word starts with the
prefix.

## Constraints
- `1 <= len(operations) <= 10^4`; words are lowercase, length `1..2000`.

## Examples
Input: `operations = [["insert","apple"],["search","apple"],["search","app"],["startsWith","app"],["insert","app"],["search","app"]]`
Output: `[null,true,false,true,null,true]`

Input: `operations = [["search","a"]]`
Output: `[false]`

Input: `operations = [["insert","ab"],["startsWith","abc"]]`
Output: `[null,false]`
