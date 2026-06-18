Implement a word dictionary and replay `operations`, returning the list of results.
Operations are `["addWord", word]` (returns `null`) and `["search", pattern]`, which
returns `true` if any stored word matches `pattern`, where `.` in the pattern matches
any single character.

## Constraints
- `1 <= len(operations) <= 10^4`
- words and patterns are lowercase letters and `.` (patterns only)

## Examples
Input: `operations = [["addWord","bad"],["addWord","dad"],["search",".ad"],["search","b.."]]`
Output: `[null,null,true,true]`
Explanation: `.ad` matches `bad`/`dad`; `b..` matches `bad`.

Input: `operations = [["addWord","a"],["search","."]]`
Output: `[null,true]`
Explanation: `.` matches `a`.
