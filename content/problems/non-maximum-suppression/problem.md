An object detector usually fires several overlapping boxes on the same object.
**Non-maximum suppression (NMS)** cleans that up: it keeps the most confident
box, throws away every box that overlaps it too much, and repeats with the most
confident box left.

A box is `[x1, y1, x2, y2]`, with $(x_1, y_1)$ the top-left corner and
$(x_2, y_2)$ the bottom-right, and $x_1 < x_2$, $y_1 < y_2$. Coordinates are
continuous, so a box's area is $(x_2 - x_1)(y_2 - y_1)$. Two boxes overlap by
their **intersection over union**:

$$
\operatorname{IoU}(A, B) = \frac{\operatorname{area}(A \cap B)}{\operatorname{area}(A) + \operatorname{area}(B) - \operatorname{area}(A \cap B)}
$$

where $A \cap B$ is the rectangle the two boxes share (area $0$ if they share
none, or only an edge).

Run greedy NMS exactly like this:

1. Rank the boxes by score, **highest first**. Boxes with **equal scores** are
   ranked by index, **lower index first**.
2. Take the highest-ranked box that is still in play and **keep** it.
3. Remove from play every remaining box whose IoU with the kept box is
   **strictly greater** than `iouThreshold`. A box whose IoU **equals** the
   threshold stays.
4. Repeat from step 2 until no boxes are left in play.

**Return the indices of the kept boxes, in the order they were kept.** (A box
that was removed never removes anything itself.)

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists.

## Constraints

- `1 <= N <= 1000`, where `N = len(boxes) = len(scores)`
- Each box is 4 finite numbers with absolute value `<= 10⁴`, and `x1 < x2`,
  `y1 < y2`
- Each score is a finite number with absolute value `<= 10⁶`
- `0 <= iouThreshold <= 1`

## Examples

**Example 1**
```
Input:  boxes = [[0, 0, 10, 10], [1, 1, 11, 11], [20, 0, 30, 10], [5, 0, 15, 10]],
        scores = [0.9, 0.8, 0.7, 0.95], iouThreshold = 0.5
Output: [3, 0, 2]
Explanation: box 3 scores highest and is kept first. Its IoU with box 0 is
50/150 ≈ 0.33 and with box 1 is 54/146 ≈ 0.37, so both stay. Box 0 is kept
next and removes box 1 (IoU 81/119 ≈ 0.68). Box 2 overlaps nothing.
```

**Example 2**
```
Input:  boxes = [[0, 0, 4, 2], [0, 0, 4, 4], [10, 10, 12, 12], [10, 10, 12, 12]],
        scores = [0.6, 0.9, 0.6, 0.6], iouThreshold = 0.5
Output: [1, 0, 2]
Explanation: box 1 is kept first. Box 0 lies inside it with IoU exactly
8/16 = 0.5, which is not greater than 0.5, so box 0 stays. Boxes 0, 2 and 3
tie at 0.6, so they come in index order: box 0, then box 2, which removes its
identical twin, box 3.
```

**Example 3**
```
Input:  boxes = [[0, 0, 4, 4], [2, 0, 6, 4], [4.5, 0, 8.5, 4], [6, 6, 8, 8]],
        scores = [0.9, 0.8, 0.7, 0.6], iouThreshold = 0.2
Output: [0, 2, 3]
Explanation: box 0 removes box 1 (IoU 8/24 ≈ 0.33). Box 1 would have removed
box 2 (IoU 6/26 ≈ 0.23), but it is already gone, so box 2 is kept. Box 3 lies
beyond box 0 in both x and y, so they do not overlap at all.
```
