Given `beginWord`, `endWord`, and a `wordList`, a transformation changes exactly
one letter at a time, and every intermediate word must be in `wordList`. Return
**the number of words in the shortest transformation sequence** from `beginWord`
to `endWord` (counting both ends), or `0` if none exists. `beginWord` need not be
in `wordList`.

## Constraints
- `1 <= len(beginWord) <= 10`; all words have the same length and are lowercase.
- `1 <= len(wordList) <= 5000`.

## Examples
Input: `beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]`
Output: `5`
Explanation: hit → hot → dot → dog → cog.

Input: `beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log"]`
Output: `0`

Input: `beginWord = "a", endWord = "c", wordList = ["a","b","c"]`
Output: `2`
