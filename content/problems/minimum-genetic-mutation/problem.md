A gene is an 8-character string over `A`, `C`, `G`, `T`. One **mutation** changes a
single character, and every intermediate gene must be in `bank`. Return the minimum
number of mutations to get from `startGene` to `endGene`, or `-1` if impossible.

## Constraints
- `startGene` and `endGene` have equal length over `ACGT`
- `0 <= len(bank) <= 10`

## Examples
Input: `startGene = "AACCGGTT", endGene = "AACCGGTA", bank = ["AACCGGTA"]`
Output: `1`
Explanation: One valid mutation reaches the end gene.

Input: `startGene = "AACCGGTT", endGene = "AAACGGTA", bank = ["AACCGGTA","AACCGCTA","AAACGGTA"]`
Output: `2`
Explanation: A shortest valid chain uses two mutations.
