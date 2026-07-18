"""Test-strengthening toolkit (see docs/test-strengthening.md).

Machine-generates candidate inputs for a problem, computes their expected values
by executing the *trusted canonical* through the real judge, and selects the few
inputs that best discriminate correct from buggy user solutions — using mutation
testing (small plausible-wrong edits of the canonical) as a proxy for the bugs
users write.

Nothing here re-implements the sandbox or the judge: expected values and mutant
grading both go through ``app.executor.run_submission`` so ``compare`` semantics
and the ``TreeNode`` codec are honored automatically.
"""
from .generators import GenConfig, generate_candidates, generate_class_candidates
from .constraints import parse_constraints
from .mutate import make_mutants
from .select import select_cases

__all__ = [
    "GenConfig",
    "generate_candidates",
    "generate_class_candidates",
    "parse_constraints",
    "make_mutants",
    "select_cases",
]
