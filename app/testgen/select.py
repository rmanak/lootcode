"""Greedy minimal-set selection over a *coverage* matrix.

Given, for each candidate input, the set of **coverage tokens** it covers, choose
the smallest set of inputs that covers every *coverable* token the existing suite
misses — i.e. the minimal set of new cases that maximally widens behavioral
coverage. Protected candidates (edge shapes and the stress input) are always
kept; the rest are added greedily by marginal new coverage.

The tokens are opaque hashables and may come from *any* universe — structural
input features (features.py), canonical execution regimes (coverage.py), output
classes, and mutant/adversary kills — all mixed into one set per input. This is
the fix to the old flaw: an input is kept because it covers new behavior, never
gated on whether a particular invented wrong solution happens to fail on it.
Mutant/adversary kills are just *one more universe* of tokens here — they can
only ever help an input get picked, never veto one.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Hashable


@dataclass
class Selection:
    chosen: list[int]                       # indices into the candidate list
    total_mutants: int                      # total coverable tokens (for reporting)
    killed_by_chosen: int                   # tokens covered by baseline + picks
    killable: int                           # tokens coverable by *some* candidate
    per_pick: list[tuple[int, int]] = field(default_factory=list)  # (cand_idx, new_cov)


def select_cases(kills: list[set[Hashable]], protected: list[int],
                 total_mutants: int, cap: int,
                 baseline: set[Hashable] | None = None,
                 sizes: list[int] | None = None) -> Selection:
    """
    ``kills[i]`` = set of coverage tokens covered by candidate ``i`` (any hashable
    tokens — mutant ids, ``feat:``/``line:``/``val:``/``out:`` strings, …).
    ``protected`` = candidate indices to force-include (kept even if 0 new tokens).
    ``cap`` = max cases to select in total.
    ``baseline`` = tokens already covered by the *existing* suite; picks only earn
    marginal credit for tokens beyond this, so we add only new discriminating cases.
    ``sizes`` = optional per-candidate size (e.g. serialized input length); among
    candidates of *equal* marginal gain, the smallest is picked, so the suite
    prefers minimal, readable inputs over sprawling ones that happen to cover the
    same new behavior.
    """
    baseline = set(baseline or ())
    all_killable: set[Hashable] = set(baseline)
    for s in kills:
        all_killable |= s

    chosen: list[int] = []
    covered: set[Hashable] = set(baseline)
    per_pick: list[tuple[int, int]] = []

    # 1) Force-include protected candidates first (T1/T4 guarantees).
    for i in protected:
        if i in chosen:
            continue
        new = kills[i] - covered
        chosen.append(i)
        covered |= kills[i]
        per_pick.append((i, len(new)))

    # 2) Greedily add the highest-marginal-gain candidate until covered or capped.
    #    Ties (equal new coverage) go to the smaller input, so the suite stays
    #    compact and readable instead of favoring sprawling max-coverage inputs.
    def _sz(i: int) -> int:
        return sizes[i] if sizes is not None else 0

    remaining = set(range(len(kills))) - set(chosen)
    while covered != all_killable and len(chosen) < cap and remaining:
        best_i, best_gain, best_sz = -1, 0, None
        for i in remaining:
            gain = len(kills[i] - covered)
            if gain > best_gain or (gain == best_gain and gain > 0
                                    and best_sz is not None and _sz(i) < best_sz):
                best_i, best_gain, best_sz = i, gain, _sz(i)
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
