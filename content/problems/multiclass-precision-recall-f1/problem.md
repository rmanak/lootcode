Build the core of a classification report for a multi-class classifier. The
classes are $0, 1, \dots, C - 1$, where $C$ = `numClasses`. You get the true
labels `yTrue` and the predicted labels `yPred` for $N$ examples; write $y_i$
for `yTrue[i]` and $\hat y_i$ for `yPred[i]`.

**Per class.** For each class $c$, treat $c$ as "positive" and every other
class as "negative". Its true positives $\mathit{tp}_c$, precision $P_c$,
recall $R_c$, F1 score $F_c$ and support $S_c$ are

$$
\begin{aligned}
\mathit{tp}_c &= \#\{\, i : y_i = c \text{ and } \hat y_i = c \,\} \\[1ex]
P_c &= \frac{\mathit{tp}_c}{\#\{\, i : \hat y_i = c \,\}} \\[1ex]
R_c &= \frac{\mathit{tp}_c}{\#\{\, i : y_i = c \,\}} \\[1ex]
F_c &= \frac{2\, P_c\, R_c}{P_c + R_c} \\[1ex]
S_c &= \#\{\, i : y_i = c \,\}
\end{aligned}
$$

Any value that would be $0 / 0$ is $0$. That includes a class nobody predicts,
a class absent from `yTrue`, and F1 when precision and recall are both 0.

**Averages** over all $C$ classes, including classes with no examples:

- **macro**: the plain mean of the per-class precision, recall and F1. Macro
  F1 is the mean of the per-class F1 values. It is **not** the F1 of macro
  precision and macro recall.
- **weighted**: the per-class precision, recall and F1 averaged with weights
  $S_c / N$
- **micro F1**: pool every class's counts before dividing. With one label per
  example, this equals the accuracy, the fraction of examples with
  $\hat y_i = y_i$.

**Return `[perClass, macro, weighted, microF1]`**:
- `perClass`: $C$ rows of `[precision, recall, f1, support]`
- `macro`: `[precision, recall, f1]`
- `weighted`: `[precision, recall, f1]`
- `microF1`: a number

Supports must match exactly. Everything else is accepted when within a
relative `1e-6` (or an absolute `1e-9`) of the expected value.

## Constraints

- `2 <= numClasses <= 20`
- `1 <= N <= 10⁴`, where `yTrue` and `yPred` both have `N` entries
- Every label is an integer in `[0, numClasses)`

## Examples

**Example 1**
```
Input:  yTrue = [0, 1, 2, 2, 1, 0], yPred = [0, 2, 2, 2, 1, 1], numClasses = 3
Output: [[[1.0, 0.5, 0.6666666666666666, 2], [0.5, 0.5, 0.5, 2], [0.6666666666666666, 1.0, 0.8, 2]],
         [0.7222222222222222, 0.6666666666666666, 0.6555555555555556],
         [0.7222222222222222, 0.6666666666666666, 0.6555555555555556],
         0.6666666666666666]
Explanation: class 0 is predicted once, correctly (precision 1), and has two
true examples (recall 1/2). Macro F1 is (2/3 + 1/2 + 4/5) / 3. Every class has
support 2, so the weighted averages equal the macro ones. 4 of the 6
predictions are right, so micro F1 is 2/3.
```

**Example 2**
```
Input:  yTrue = [0, 0, 1, 1], yPred = [0, 0, 0, 0], numClasses = 2
Output: [[[0.5, 1.0, 0.6666666666666666, 2], [0.0, 0.0, 0.0, 2]],
         [0.25, 0.5, 0.3333333333333333], [0.25, 0.5, 0.3333333333333333], 0.5]
Explanation: nothing is predicted as class 1, so its precision is 0 / 0 = 0.
```

**Example 3**
```
Input:  yTrue = [0, 1, 0, 1], yPred = [0, 1, 0, 1], numClasses = 4
Output: [[[1.0, 1.0, 1.0, 2], [1.0, 1.0, 1.0, 2], [0.0, 0.0, 0.0, 0], [0.0, 0.0, 0.0, 0]],
         [0.5, 0.5, 0.5], [1.0, 1.0, 1.0], 1.0]
Explanation: classes 2 and 3 never occur, but they still count in the macro
average, and they pull it down to 0.5. Their support is 0, so they add nothing
to the weighted average.
```
