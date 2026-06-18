Validate a code snippet against these rules: it must be wrapped in one closed tag
`<TAG_NAME>...</TAG_NAME>` (matching names); a valid `TAG_NAME` is 1-9 upper-case
letters; tag content may contain nested valid closed tags, `cdata`, and any
characters except an unmatched `<`, an unmatched tag, or a closed tag with an invalid
name; `<![CDATA[ ... ]]>` content (up to the first `]]>`) is treated as raw text.
**Return `true` if the snippet is valid.**

**Examples**
```
"<DIV>This is the first line <![CDATA[<div>]]></DIV>"  ->  true
"<A>  <B> </A>   </B>"                                 ->  false
"<DIV>  unmatched <  </DIV>"                           ->  false
```

**Constraints:** the snippet uses only letters, digits, and `<>/![] ` (space).
