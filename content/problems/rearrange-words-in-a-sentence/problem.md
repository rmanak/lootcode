`text` is a sentence: space-separated words, the first word capitalised and every
other character lowercase. Rearrange the words in **increasing order of their
length**; words of equal length keep their original relative order (a stable
sort). Re-emit the result in the same format: capitalise only the first letter of
the new sentence and lowercase the rest.

**Examples**
```
text = "Leetcode is cool"        ->  "Is cool leetcode"
text = "Keep calm and code on"   ->  "On and keep calm code"
text = "To be or not to be"      ->  "To be or to be not"
```

**Constraints:** `text` begins with a capital letter followed by lowercase letters
and single spaces, `1 <= len(text) <= 10^5`.
