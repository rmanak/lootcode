Each log is a space-separated string whose first token is an identifier. A
**letter-log** has words after the identifier; a **digit-log** has only digits.
Reorder so all letter-logs come first, sorted by content (then by identifier to
break ties), followed by the digit-logs in their **original** order.

## Constraints
- `1 <= len(logs) <= 100`
- each log has an identifier followed by content that is all letters or all digits

## Examples
Input: `logs = ["d1 8 1","l1 art can","l2 art zero"]`
Output: `["l1 art can","l2 art zero","d1 8 1"]`
Explanation: Letter-logs sorted by content, then the digit-log.

Input: `logs = ["a1 9 2","g1 act car"]`
Output: `["g1 act car","a1 9 2"]`
Explanation: The letter-log moves ahead of the digit-log.
