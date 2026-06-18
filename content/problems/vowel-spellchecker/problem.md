Given a `wordlist`, build a spellchecker that maps each query word to a correct word
using this precedence:

1. **Exact match** (case-sensitive): return the query unchanged.
2. **Capitalization**: if the query matches a wordlist word ignoring case, return the
   first such wordlist word.
3. **Vowel error**: treating every vowel (`a, e, i, o, u`) as interchangeable and
   ignoring case, if the query matches a wordlist word, return the first such word.
4. Otherwise return the empty string `""`.

Return `answer`, where `answer[i]` is the correct word for `queries[i]`.

**Example**
```
wordlist = ["KiTe","kite","hare","Hare"]
queries  = ["kite","Kite","KiTe","Hare","HARE","Hear","hear","keti","keet","keto"]
   ->  ["kite","KiTe","KiTe","Hare","hare","","","KiTe","","KiTe"]
```

**Constraints:** `1 <= len(wordlist), len(queries) <= 5000`; word lengths in `[1, 7]`;
letters only.
