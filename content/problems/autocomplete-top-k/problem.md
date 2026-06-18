Replay `operations` against an autocomplete index and return **the list of
results**. Operations are `["add", sentence, count]` → `null` (adds `count` to the
sentence's historical frequency), and `["query", prefix]` → the list of up to `k`
sentences that start with `prefix`, ranked by **frequency descending, then
lexicographically ascending**.

## Constraints
- `1 <= k <= 10`, `1 <= len(operations) <= 10^4`.
- Sentences are non-empty lowercase strings (spaces allowed); `1 <= count <= 10^6`.

## Examples
Input: `k = 2, operations = [["add","ice cream",3],["add","icing",2],["add","igloo",5],["query","i"],["query","ic"]]`
Output: `[null,null,null,["igloo","ice cream"],["ice cream","icing"]]`

Input: `k = 2, operations = [["add","cat",1],["add","car",1],["query","ca"]]`
Output: `[null,null,["car","cat"]]`
Explanation: equal frequency, so lexicographic order wins.

Input: `k = 1, operations = [["query","z"]]`
Output: `[[]]`
