WordPiece-style tokenizers encode text **greedily**: from the current
position, take the **longest** vocabulary entry that matches the text there,
emit its id, and continue after it. Implement this tokenizer.

`vocab` maps strings (tokens) to integer ids. Scan `text` from left to right.
At each position:

- If one or more vocabulary tokens match the text starting there, take the
  **longest** one, append its id, and advance past it.
- Otherwise append `unkId` and advance by **one character**.

With `mergeUnk` true, a run of consecutive unknown characters produces a
single `unkId` instead of one per character. (An unknown run ends at the next
position where some token matches.)

**Return** the list of ids.

The longest match matters: taking the first or the shortest match can split a
word that the vocabulary knows whole, or strand characters that only a longer
token covers. For speed, note that no match can be longer than the longest
vocabulary token, so only a bounded number of candidates need checking at each
position; a trie works as well. A text can be $10^5$ characters long.

## Constraints

- `0 <= len(text) <= 10⁵`; `text` is printable ASCII (spaces included)
- `1 <= len(vocab) <= 10⁴`; every token is a non-empty printable ASCII string
  of at most `20` characters
- Ids, and `unkId`, are integers in `[-10⁹, 10⁹]` (several tokens may share an id)

## Examples

**Example 1**
```
Input:  text = "apple", vocab = {"app": 1, "apple": 2}, unkId = -1, mergeUnk = false
Output: [2]
Explanation: both "app" and "apple" match at position 0; the longer one wins.
Taking "app" would leave "le", which the vocabulary cannot encode.
```

**Example 2**
```
Input:  text = "appbbbapp", vocab = {"app": 1, "apple": 2}, unkId = -1, mergeUnk = true
Output: [1, -1, 1]
Explanation: no token starts with "b", so each b is unknown. With mergeUnk
the run of three becomes a single -1 (without it the answer is
[1, -1, -1, -1, 1]).
```

**Example 3**
```
Input:  text = "abczzab", vocab = {"a": 1, "ab": 2, "abc": 3, "bca": 4, "c": 5}, unkId = 0, mergeUnk = false
Output: [3, 0, 0, 2]
Explanation: "abc" is the longest match at position 0. Each z is unknown and,
with mergeUnk false, emits its own 0. Then "ab" is the longest match.
```
