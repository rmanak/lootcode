"""The optional PyTorch runtime (problems with ``"runtime": "torch"``).

Kept apart from the Python runtime on purpose: torch lives in its own
interpreter (``settings.TORCH_PYTHON``, by default ``./.venv-torch``), runs
under its own memory floor, and grades against the canonical as a live oracle
on inputs that may be random. A plain problem never imports any of this.

* :mod:`.inputs`  — literal / random test inputs, made concrete (parent, no torch)
* :mod:`.compare` — ``torch.allclose`` semantics over JSON (parent, no torch)
* :mod:`.grader`  — two sandboxes (submission, canonical), compare, score
* :mod:`.harness` — the in-sandbox adapter over the core harness

See docs/torch-runtime.md.
"""
from __future__ import annotations

import os
import subprocess
import threading

from ...config import settings

_probe_lock = threading.Lock()
_probed_ok: set[str] = set()


def unavailable_reason() -> str | None:
    """Why torch problems cannot run here, or ``None`` when they can.

    On the subprocess backend the interpreter must exist and import torch. The
    import probe costs about a second, so a *success* is remembered for the life
    of the process; a failure is not, so installing the environment while the
    server runs is picked up on the next submission. On the docker backend the
    runner image must be built (`infra/runner-torch.Dockerfile`).
    """
    if settings.EXECUTOR_BACKEND == "docker":
        return _docker_image_missing(settings.TORCH_DOCKER_IMAGE)
    py = settings.TORCH_PYTHON
    if py in _probed_ok:
        return None
    if not (os.path.isfile(py) and os.access(py, os.X_OK)):
        return f"no torch interpreter at {py} (run `make torch-env`)"
    with _probe_lock:
        if py in _probed_ok:
            return None
        try:
            r = subprocess.run(  # noqa: S603 - fixed argv, our own interpreter
                [py, "-I", "-c", "import torch"], capture_output=True, timeout=60,
                check=False, env={"PATH": "/usr/bin:/bin", "OMP_NUM_THREADS": "1",
                                  "MKL_NUM_THREADS": "1"})
        except (OSError, subprocess.SubprocessError) as exc:
            return f"{py} could not be started: {exc}"
        if r.returncode != 0:
            tail = (r.stderr or b"").decode("utf-8", "replace").strip().splitlines()
            return f"{py} cannot import torch ({tail[-1] if tail else 'no output'})"
        _probed_ok.add(py)
    return None


def _docker_image_missing(image: str) -> str | None:
    """On the docker backend: is the torch runner image built? Remembered once
    it is; `docker_command` uses `--pull never`, so a missing one fails closed."""
    if image in _probed_ok:
        return None
    try:
        r = subprocess.run(["docker", "image", "inspect", image],  # noqa: S603, S607
                           capture_output=True, timeout=30, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        return f"docker is not usable here ({exc})"
    if r.returncode != 0:
        return (f"docker image {image!r} is not built "
                "(docker build -f infra/runner-torch.Dockerfile -t lootcode-runner-torch .)")
    _probed_ok.add(image)
    return None
