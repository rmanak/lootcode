Given a string `chars`, compress it by replacing each maximal run of a repeated
character with that character followed by the run length **when the run length is
greater than 1**. Return **the compressed string**. A run of length 1 is written
as just the character.

## Constraints
- `0 <= len(chars) <= 10^5`, lowercase/uppercase letters and digits.

## Examples
Input: `chars = "aabbccc"`
Output: `"a2b2c3"`

Input: `chars = "abc"`
Output: `"abc"`

Input: `chars = "aaa"`
Output: `"a3"`
