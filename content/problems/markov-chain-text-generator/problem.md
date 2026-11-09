The simplest language model is a **first-order Markov chain over words**: the
next word depends only on the current one, with probabilities proportional to
how often each word followed it in the training text. Build one from `corpus`
and use it to generate text.

**Tokenize.** Lowercase the corpus, replace every character that is not a
letter `a`–`z`, a digit or an apostrophe `'` with a space, and split on
whitespace. That gives one sequence of words $w_1, \dots, w_N$; sentence
boundaries are ignored, so the last word of one sentence is followed by the
first word of the next.

**Count.** For every adjacent pair $(w_k, w_{k+1})$, count one transition from
$w_k$ to $w_{k+1}$. The **followers** of a word are the words it has
transitions to, each with its count. The final word of the corpus has no
transition out (unless it also appears earlier).

**Generate.** Start from `startWord`, lowercased (it is a single word with no
punctuation). Take `steps` steps; each step moves from the current word to one
of its followers and appends it. If the current word has no followers (it is
unseen, or occurs only at the very end), stop early. The next word is chosen
in one of two modes:

- **Greedy** (`draws` is empty): the most frequent follower. On a tie, the
  alphabetically smallest word.
- **Sampled** (`draws` has exactly `steps` numbers in $[0, 1)$): list the
  followers in **alphabetical order** with probabilities $c_f / C$ (their counts
  over the total count $C$), and pick the first follower whose cumulative
  probability exceeds $u$ = `draws[step]`. That is the inverse-CDF method: a
  follower with probability $0.25$ is picked for a quarter of the possible
  draws. Step $t$ (from $0$) uses `draws[t]`, so after an early stop the
  remaining draws go unused. (No draw lies within $10^{-9}$ of a cumulative
  boundary.)

**Return** the generated words, starting with the lowercased `startWord`.

## Constraints

- `1 <= len(corpus) <= 2·10⁵`, printable ASCII
- `startWord` is a non-empty string of letters, digits and apostrophes
- `0 <= steps <= 1000`
- `draws` is empty or has exactly `steps` numbers, each in `[0, 1)`

## Examples

**Example 1**
```
Input:  corpus = "The sky is blue and this water is blue and the grass is green.", startWord = "the",
        steps = 6, draws = []
Output: ["the", "grass", "is", "blue", "and", "the", "grass"]
Explanation: "the" is followed once each by "sky" and "grass" (the first
"The" is lowercased), and the tie goes to "grass". "is" is followed by "blue"
twice and "green" once, so greedy takes "blue". "and" ties between "this" and
"the", and "the" is alphabetically first.
```

**Example 2**
```
Input:  corpus = "The sky is blue and this water is blue and the grass is green.", startWord = "and",
        steps = 4, draws = [0.2, 0.7, 0.4, 0.1]
Output: ["and", "the", "sky", "is", "blue"]
Explanation: "and" → followers in alphabetical order "the" (cumulative 0.5),
"this" (1.0); 0.2 < 0.5 picks "the". From "the": "grass" (0.5), "sky" (1.0);
0.7 picks "sky". "sky" has one follower. From "is": "blue" (2/3), "green" (1);
0.4 picks "blue".
```

**Example 3**
```
Input:  corpus = "Don't stop. Don't STOP believing! Hold on.", startWord = "DON'T", steps = 3, draws = []
Output: ["don't", "stop", "believing", "hold"]
Explanation: apostrophes stay inside words, and case and punctuation are
dropped. "stop" is followed once by "don't" (across the sentence boundary) and
once by "believing"; the tie goes to "believing".
```
