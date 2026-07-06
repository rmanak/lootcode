"""Greedy minimal-set selection from a mutation-kill matrix (technique T5).

Given, for each candidate input, the set of mutant ids it kills, choose the
smallest set of inputs that kills every *killable* mutant — i.e. the minimal
discriminating suite. Protected candidates (T1 edge shapes and the T4 stress
input) are always kept; the rest are added greedily by marginal kills.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Selection:
    chosen: list[int]                       # indices into the candidate list
    total_mutants: int
    killed_by_chosen: int
    killable: int                           # mutants killed by *some* candidate
    per_pick: list[tuple[int, int]] = field(default_factory=list)  # (cand_idx, new_kills)


def select_cases(kills: list[set[int]], protected: list[int],
                 total_mutants: int, cap: int,
                 baseline: set[int] | None = None) -> Selection:
    """
    ``kills[i]`` = set of mutant ids killed by candidate ``i``.
    ``protected`` = candidate indices to force-include (kept even if 0 kills).
    ``cap`` = max cases to select in total.
    ``baseline`` = mutants already killed by the *existing* suite; picks only earn
    marginal credit for mutants beyond this, so we add only new discriminating cases.
    """
    baseline = set(baseline or ())
    all_killable: set[int] = set(baseline)
    for s in kills:
        all_killable |= s

    chosen: list[int] = []
    covered: set[int] = set(baseline)
    per_pick: list[tuple[int, int]] = []

    # 1) Force-include protected candidates first (T1/T4 guarantees).
    for i in protected:
        if i in chosen:
            continue
        new = kills[i] - covered
        chosen.append(i)
        covered |= kills[i]
        per_pick.append((i, len(new)))

    # 2) Greedily add the highest-marginal-kill candidate until covered or capped.
    remaining = set(range(len(kills))) - set(chosen)
    while covered != all_killable and len(chosen) < cap and remaining:
        best_i, best_gain = -1, 0
        for i in remaining:
            gain = len(kills[i] - covered)
            if gain > best_gain:
                best_i, best_gain = i, gain
        if best_gain == 0:
            break
        chosen.append(best_i)
        covered |= kills[best_i]
        remaining.discard(best_i)
        per_pick.append((best_i, best_gain))

    return Selection(
        chosen=chosen,
        total_mutants=total_mutants,
        killed_by_chosen=len(covered),
        killable=len(all_killable),
        per_pick=per_pick,
    )
