Mask a personal-information string. **Email** (`name1@name2.name3`): lowercase
everything and replace the middle of `name1` with exactly `5` asterisks
(`l*****e@...`). **Phone** (digits plus `+ - ( ) ` and spaces, 10-13 digits): keep
only the last `4` digits as `***-***-1111`; if there is a country code of `k` digits,
prefix `+` then `k` stars then `-`. **Return the masked string.**

**Examples**
```
"LeetCode@LeetCode.com"  ->  "l*****e@leetcode.com"
"1(234)567-890"          ->  "***-***-7890"
"86-(10)12345678"        ->  "+**-***-***-5678"
```

**Constraints:** `len(S) <= 40`; a valid email or phone number.
