# The PyTorch runtime

Some ML interview questions are *about* PyTorch: "implement the CLIP loss",
"write scaled dot-product attention", "write this layer's forward pass". A
problem whose `meta.json` says `"runtime": "torch"` is graded by a separate
interpreter that has PyTorch installed. The solver gets real tensors and
returns real tensors, and the answer is checked with `torch.allclose`
semantics against the reference solution.

Every other problem is untouched. It runs under the `"python"` runtime, the
same interpreter, harness, limits and comparison as before, and it never
imports any of this. Pilot problem: `content/problems/clip-loss-pytorch/`.

## Installing it

```bash
make torch-env          # ./.venv-torch: Python 3.12 + CPU-only torch (requirements-torch.txt)
```

That's all. The app finds the interpreter at `./.venv-torch/bin/python`
(override with `LOOTCODE_TORCH_PYTHON`). Without it, torch problems still list
and render. A Run reports that the PyTorch runtime is not installed, and
`seed.py` / `verify_bank.py` / `audit.py` **skip** them with that reason
instead of reporting a broken canonical. So a fresh clone without torch
stays green.

Why a separate interpreter rather than `pip install torch` into `./.venv`:

- **The web app never imports torch.** Its environment stays at ~0.5 GB
  instead of ~1.7 GB, and nothing the app depends on is pinned by torch's
  requirements.
- **Plain problems pay nothing.** They keep their 512 MB address-space cap
  and their ~50 ms run. A torch run imports torch (~0.7 s) and needs a larger
  cap, and only torch problems pay for that.
- **CPU-only wheels.** The sandbox gets no GPU, by design: a submission must
  not reach the GPU driver, and both GPUs belong to other work. The CPU wheel
  is the one that fits a sandbox. Measured on torch 2.15.0+cpu, `import torch`
  dies with `std::bad_alloc` under a 512 MB `RLIMIT_AS`, succeeds at 768 MB,
  and peaks at ~305 MB resident. The CUDA build needed ~4 GB of address space
  just to import, which is why `docs/ml-coding-plan.md` §2 left torch out.

## How a torch problem is graded

```
            parent (web app, no torch)
  stored tests ──┐
  generator  ────┼─► concrete inputs (stdlib PRNG, seeded)
                 │         │                         │
                 │   sandbox A: submission     sandbox B: canonical
                 │   (.venv-torch, -I)         (.venv-torch, -I)
                 │         │ JSON out                │ JSON out
                 └────────►└──── allclose here ◄─────┘
```

1. **Inputs are made concrete in the parent** (`app/executor/torch_runtime/inputs.py`).
   A random tensor is drawn with Python's `random`, not `torch.randn`. The
   parent has no torch, and the same numbers go to both sandboxes byte for
   byte, independent of the torch version or which process drew them.
2. **The canonical is a live oracle.** The submission and the canonical run
   in two separate sandboxes, in parallel, on identical inputs. The canonical
   is never in the submission's process or run directory. On the subprocess
   backend it can still be read from disk; see "Trust model".
3. **Comparison happens in the parent** (`compare.py`) with `torch.allclose`
   semantics, re-implemented without torch:
   `|actual − expected| ≤ atol + rtol·|expected|` element-wise. On top of
   that, **shape and dtype must match exactly** (no broadcasting; a float64
   answer to a float32 question is a different answer), integer/bool tensors
   compare exactly, `NaN` matches `NaN`, and `inf` matches only the same `inf`.
   Defaults are `rtol=1e-5` (torch's) and `atol=1e-6`. Torch's default
   `atol=1e-8` is below float32 resolution near zero.
4. A wrong answer says why: `shape (1,), expected ()`, `dtype float64, expected
   float32`, or `3 of 12 values differ; worst at [1, 2]: got 0.51, expected
   0.48`. The run endpoint shows that text only for visible tests, as before.
   Hidden tests show pass/fail only.

When the code being graded *is* the canonical (seed, `verify_bank`, admin
verify), one run serves as both. That check proves the canonical runs on
every input without error. Its correctness is the author's job; see
"Authoring" below.

## Writing a torch problem

`meta.json`: the usual fields, plus `runtime` and a `torch` block.

```jsonc
{
  "function": {"name": "clip_loss",
               "params": [{"name": "image_feat", "type": "Tensor"},
                          {"name": "text_feat",  "type": "Tensor"},
                          {"name": "temperature","type": "float"}],
               "returns": {"type": "Tensor"}},
  "compare": "close",              // informational; torch problems always use allclose
  "limits": {"timeLimitMs": 5000, "memoryLimitMb": 2048},
  "runtime": "torch",
  "torch": {
    "rtol": 1e-5, "atol": 1e-6,    // optional; these are the defaults
    "random_tests": 5,             // fresh hidden tests drawn on EVERY run
    "dims": {"N": [1, 32], "D": [2, 64]},        // drawn once per test
    "inputs": {                    // the generator: one value spec per parameter
      "image_feat": {"$random": {"shape": ["N", "D"], "dist": "randn",
                                 "mean": [-2, 2], "std": [0.5, 10]}},
      "text_feat":  {"$random": {"shape": ["N", "D"], "dist": "randn"}},
      "temperature": {"$random": {"dist": "choice", "values": [0.01, 0.07, 1.0]}}
    }
  }
}
```

**Types.** A parameter typed `Tensor` arrives as a `torch.Tensor`, and `Tensor[]`
as a list of them. Every other parameter arrives as plain JSON, as on the Python
runtime. The return value may be a tensor, a Python number, or any
list/tuple/dict of those. A tuple compares like a list. `torch` is injected
into the solution's globals (as `TreeNode` is for tree problems), so a solver
who forgets `import torch` is not failed for it. Default dtype is **float32**.

**Test values** (in `tests/cases.json` and in `torch.inputs`), per parameter:

| value | becomes |
|---|---|
| a number or rectangular nested list | a float32 tensor of that shape (for a `Tensor` param), else the plain value |
| `{"$tensor": {"data": …, "shape"?: […], "dtype"?: "int64", "requires_grad"?: true}}` | a literal with an explicit dtype/shape |
| `{"$random": {"shape": [8, "D"], "dist": …, …}}` | a random tensor (a nested list for a non-tensor param) |
| `{"$random": {"dist": …}}` (no `shape`) | a random scalar (a 0-dim tensor for a `Tensor` param) |

Distributions: `randn`/`normal` (`mean`, `std`), `rand`/`uniform` (`low`,
`high`; half-open), `randint` (integer `low`, `high`, exclusive, defaults to
int64), `bernoulli` (`p`, defaults to bool), `choice` (`values`). Any numeric
distribution parameter may be a `[lo, hi]` pair, drawn once per test. So
`"std": [0.5, 10]` covers features at many scales instead of one. `"dtype"`
overrides the default, `"round": k` rounds a scalar, and `"seed"` pins the draw.
Two parameters with the same spec and the same pinned seed get **identical**
tensors, which is how the pilot builds "perfectly aligned pairs".

dtypes: `float32 float64 float16 bfloat16 int64 int32 int16 int8 uint8 bool`.
Only these names are ever looked up on the torch module.

**Stored tests** keep `expected: null`, because the canonical is the oracle. A
`$random` value in a stored test is seeded from the test's *name*, so a stored
test is the same test on every run and every machine. Shapes in stored tests
are concrete ints. Symbolic dims (`"N"`) belong to the generator.

**Random tests.** `random_tests` hidden tests named `random-1…k` are drawn on
every run from a fresh seed. Each submission meets inputs no earlier one saw.
That is the point: an overfit or edge-case-blind solution cannot settle into
passing a fixed suite. It also means a borderline-wrong solution can pass one
run and fail the next, which is the honest result. `random_weight` (default 1)
weights them.

**Size.** Every input is built in the web server's own process before any
sandbox starts, so it is bounded there:

- at most 50,000 numbers per test (counting every dim as at least 1, so a
  zero-size dim cannot smuggle in a huge structure);
- 500,000 per run;
- 200 tests per run;
- `random_tests` ≤ 50.

A returned tensor is refused past 200,000 elements, checked before a sparse
answer is densified. The whole run's result shares the
~1 MB result budget (`docs/code-execution.md`). Tests are meant to be small:
a 64×128 input catches everything a 4096×4096 one would, and the per-test
alarm cannot interrupt a long torch kernel (the same caveat as numpy).

### Authoring checklist

The grader cannot tell you the canonical is *right*, only that it runs. So,
before publishing:

1. **Independent implementations agree.** Write two or three correct
   solutions that differ in op order (a fused library call, a manual
   `logsumexp`, a float64 computation cast back) and check they match the
   canonical within the tolerance over the stored tests **and** a few thousand
   generator draws. If any draw disagrees, the problem is ill-conditioned there,
   so tighten the generator. The pilot's script used 9% of the tolerance at
   worst.
2. **Typical wrong answers fail.** Missing normalization, one direction
   instead of two, `·τ` instead of `/τ`, sum instead of mean, the naive
   `exp` that overflows. Each needs at least one *stored* hidden test that
   catches it deterministically. Random tests are a bonus, not the guarantee.
3. **The validator holds the generator to the constraints.**
   `scripts/check_constraint_validators.py` makes torch inputs concrete
   (tensors → nested lists) and runs `validate_input` over the stored tests
   **plus 300 generator draws**. A generator that can produce an input the
   statement rules out fails here.
4. `make check` (seed, audit, math, verify_bank, validators).

## Limits and settings

| setting | default | meaning |
|---|---|---|
| `LOOTCODE_TORCH_PYTHON` | `./.venv-torch/bin/python` | the torch interpreter (subprocess backend) |
| `EXEC_TORCH_MEMORY_LIMIT_MB` | 2048 | `RLIMIT_AS` floor for a torch run; a problem's `memoryLimitMb` can raise it, never lower it |
| `EXEC_TORCH_STARTUP_S` | 30 | wall-clock allowance for `import torch`, added to the run's budget |
| `EXEC_TORCH_MEMORY_LIMIT_MAX_MB` | 8192 | the most a problem's `memoryLimitMb` may raise it to |
| `EXEC_TORCH_MAX_PARALLEL` | 4 | torch sandboxes alive at once, server-wide (each Run starts two) |
| `EXEC_TORCH_DOCKER_IMAGE` | `lootcode-runner-torch` | the image on the docker backend (`infra/runner-torch.Dockerfile`); run with `--pull never`, so a missing image fails closed |

The torch harness pins torch to one intra-op and one inter-op thread, and the
sandbox already sets `OMP_NUM_THREADS=MKL_NUM_THREADS=1`. This gives
deterministic float reductions and spends the CPU budget one core at a time.
It also seeds torch's RNG to 0. No graded answer may depend on torch's RNG,
because the submission and canonical run in different processes.

## How it is built (and why it can't hurt the Python runtime)

| file | runs in | role |
|---|---|---|
| `app/executor/torch_runtime/inputs.py` | parent | literal / `$random` values → concrete JSON (stdlib only) |
| `app/executor/torch_runtime/compare.py` | parent | allclose over JSON; validates the untrusted side's structure first |
| `app/executor/torch_runtime/grader.py` | parent | two sandboxes in parallel, compare, score → the same `GradedRun` as the Python runtime |
| `app/executor/torch_runtime/harness.py` | sandbox | loads the **core** harness, registers a `Tensor` codec, calls the core `main()` |

The touch points in the core are small and additive. `ProblemView` gained
three defaulted fields. `run_submission` has one branch, `runtime == "torch"`,
which imports the grader lazily. `sandbox.run_harness` takes an optional
`python=` / `image=` that change *which* interpreter runs, never the limits,
environment or teardown. There are two DB columns (`runtime` default
`'python'`, `runtime_config`) with an additive migration. `meta.json` gets
`runtime`/`torch` keys, written only when non-default, so a plain problem's
file is byte-identical. A test (`test_grading_a_python_problem_never_imports_the_torch_runtime`)
pins that a plain problem never loads the torch runtime.

The in-sandbox side is deliberately not a second harness. The parent ships the
exact `app/executor/harness.py` every Python problem runs into the run
directory, and the adapter loads it *before* the solution. Output capping, the
per-test alarm, the solution loader and the result writer's degradation
ladder are therefore the same code, and a torch result is read back by the
same hardened `sandbox.read_results`.

## Trust model

Same as the rest of the executor (`docs/code-execution.md`,
`docs/security.md`): the **process and its limits** are the boundary. Torch
does not widen it. A submission could already load native code through
`ctypes`, and it gets the same rlimits, process group, environment and
throwaway directory.

What the oracle design adds is that **expected values are computed by code**.
On the **docker** backend each container mounts only its own run directory and
has its own PID namespace, so the submission cannot see or touch the
canonical's run. On the **subprocess** backend both sandboxes run as the
server's uid, so the canonical is **readable** there:

- A submission can read `content/problems/<slug>/solution/solution.py` off
  disk, or the concurrent canonical run's directory.
- The security review demonstrated a wrong solution scoring 100/100 by
  `exec`ing the sibling run's `solution.py`.

Running the canonical first and sequentially would close nothing. The source
is on disk anyway, and a same-uid process can already write `.venv-torch`'s
site-packages or `lootcode.db`. The same is true of every Python problem's
`tests/cases.json`, so this is no new exposure. That backend is for a
personal, single-user instance, where the only person who could cheat is the
one practising. Use the docker backend if submissions come from people you
don't trust.

The reference solution's own errors are logged server-side and never shown
to the solver, because its traceback quotes its source.

## Not yet (deliberately)

- **Gradient / autograd checks** ("does the gradient flow", "write a custom
  `autograd.Function`"). The value-spec format already carries
  `requires_grad`, so a problem can return `(loss, x.grad)` today. A judge
  that *calls* the submission's `backward` is the custom-judge work in
  `docs/ml-coding-todo.md`.
- **`nn.Module` problems** (`kind: "class"` with tensor methods). The codec is
  registered for class problems too, but a class test's input is
  `{operations, args}`, which the input materializer does not walk. So literal
  tensors there work, and `$random` specs do not yet.
- **Caching the canonical's outputs** for stored tests. Today it reruns on
  every submission (in parallel, ~0.9 s total per Run). A cache keyed by
  canonical hash + input hash + torch version would halve the CPU, but it isn't
  needed at one user.
- **Docker.** `infra/runner-torch.Dockerfile` builds the image, but it has not
  been exercised the way the subprocess backend has.
