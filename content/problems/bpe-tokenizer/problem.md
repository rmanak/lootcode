# BPE Tokenizer: Learn Merges and Encode

**Byte-pair encoding (BPE)** is how GPT-style models build their vocabulary.
It starts from single characters and repeatedly **merges the most frequent
adjacent pair of symbols** into a new symbol. Common words end up as one token
and rare words split into familiar pieces.

**Learning.** `corpus` is a list of words. A word that appears several times
counts once per appearance. Each word starts as a list of its characters, and
words are never merged with each other. Repeat `numMerges` times:

1. Count every adjacent pair of symbols, over every word, weighted by how often
   the word appears. Every position counts, so the symbols `a a a` contain the
   pair `(a, a)` twice.
2. Pick the pair with the **highest count**. Break ties by the **smallest
   pair**: compare the left symbols as strings, and if they are equal, compare
   the right symbols.
3. Record the merge `[left, right]`, and in every word replace each occurrence
   of `left` immediately followed by `right` with the single symbol
   `left + right`. Scan each word **left to right**, so `a a a` merged on
   `(a, a)` becomes `aa a`.

If at some point no word has two or more symbols, there are no pairs left: stop
early with fewer merges.

**Encoding.** To tokenize `word`, start from its characters and apply the learned
merges **in the order they were learned**, each one to the whole word, scanning
left to right as above. Characters that never appeared in the corpus just stay
as single-character tokens.

**Return `[merges, tokens]`**: the list of learned merges (each `[left, right]`)
and the tokens of `word`.

You may use **numpy** and the Python standard library, but plain Python is all
you need.

## Constraints

- `1 <= len(corpus) <= 300`, and every word is 1 to 20 lowercase letters `a–z`
- `0 <= numMerges <= 200`
- `word` is 1 to 30 lowercase letters `a–z`

## Examples

**Example 1**
```
Input:  corpus = ["low", "low", "low", "lower", "newest", "newest", "widest"],
        numMerges = 4, word = "lowest"
Output: [[["l", "o"], ["lo", "w"], ["e", "s"], ["es", "t"]], ["low", "est"]]
Explanation: (l, o) and (o, w) both occur 4 times (3 in "low", 1 in "lower"),
and (l, o) is the smaller pair. Next comes (lo, w), with 4. Then (e, s) and
(s, t) tie at 3 (2 from "newest", 1 from "widest") and (e, s) wins, followed by
(es, t). "lowest" encodes as low + est.
```

**Example 2**
```
Input:  corpus = ["aaab", "aaa", "ab", "ab"], numMerges = 3, word = "aaaaab"
Output: [[["a", "a"], ["a", "b"], ["aa", "a"]], ["aa", "aa", "ab"]]
Explanation: (a, a) occurs 2 times in "aaab" and 2 in "aaa", 4 in all, beating
(a, b) at 3. Merging left to right turns "aaab" into aa a b and "aaa" into
aa a. Then (a, b) has 3, and finally (aa, a) and (aa, ab) tie at 1, and
(aa, a) is smaller. Encoding "aaaaab": aa aa a b, then aa aa ab, and (aa, a)
no longer applies.
```

**Example 3**
```
Input:  corpus = ["cab", "abc", "bca"], numMerges = 2, word = "abcab"
Output: [[["a", "b"], ["ab", "c"]], ["abc", "ab"]]
Explanation: (a, b), (b, c) and (c, a) all occur twice; (a, b) is the smallest.
After that merge, four pairs occur once each, and (ab, c) is the smallest.
```
