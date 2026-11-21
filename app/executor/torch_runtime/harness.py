"""Torch-runtime harness — runs INSIDE the sandbox, under the torch interpreter.

Trusted code (part of the sandbox boundary), and deliberately thin. It is the
core harness (``app/executor/harness.py``) plus one codec:

1. load the core harness from ``<workdir>/_lc_core_harness.py`` — the parent
   ships the exact file every Python problem runs, so output capping, the
   per-test alarm, the solution loader, the result writer and its degradation
   ladder are the *same code*, not a second copy of a security control;
2. ``import torch`` and pin it to one thread (deterministic float reductions,
   and a run spends its CPU budget one core at a time);
3. register a ``Tensor`` codec in the core harness's ``_CODECS`` table: test
   values ``{"$tensor": {shape, dtype, data}}`` become real tensors on the way
   in, and anything returned — a tensor, or tuples/lists/dicts of them — comes
   back out as the same JSON form;
4. hand control to the core harness's ``main()``.

Both are loaded before the solution runs, so nothing the submission does can
change them for this run. Must not import anything from the ``app`` package
(it is not on the path here): stdlib and torch only.
"""
from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import sys
import traceback

#: Kept in step with ``inputs.DTYPES`` (this file cannot import it). Only these
#: names are ever looked up on the torch module.
_DTYPE_NAMES = ("float32", "float64", "float16", "bfloat16",
                "int64", "int32", "int16", "int8", "uint8", "bool")
_TENSOR_TYPES = ("Tensor", "Tensor[]")
#: A returned tensor larger than this is refused rather than serialized: the
#: whole run's result.json is capped at ~1 MB (sandbox.RESULT_HEADROOM_BYTES).
_MAX_RETURN_ELEMENTS = 200_000


def _load_core(workdir: str):
    path = os.path.join(workdir, "_lc_core_harness.py")
    spec = importlib.util.spec_from_file_location("_lc_core_harness", path)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _make_codec(torch):
    dtypes = {name: getattr(torch, name) for name in _DTYPE_NAMES}

    def decode(value):
        if isinstance(value, dict) and "$tensor" in value:
            t = value["$tensor"]
            x = torch.tensor(t["data"], dtype=dtypes[t.get("dtype", "float32")])
            x = x.reshape(t["shape"])
            if t.get("requires_grad"):
                x.requires_grad_(True)
            return x
        return torch.tensor(value, dtype=torch.float32)

    def decode_list(value):
        return [decode(v) for v in value]

    def encode(value):
        """Tensors -> ``{"$tensor": ...}``; containers walked; the rest as-is
        (the core harness's JSON gate still judges it). Runs under the per-test
        alarm, so a cyclic container hits RecursionError, not a hang."""
        if isinstance(value, torch.Tensor):
            t = value.detach()
            # Size first: densifying a sparse (200000, 200000) answer would try
            # to allocate 160 GB before any later check could refuse it.
            if t.numel() > _MAX_RETURN_ELEMENTS:
                raise ValueError(f"returned tensor has {t.numel()} elements; "
                                 f"answers are capped at {_MAX_RETURN_ELEMENTS}")
            if t.is_complex():
                raise ValueError("complex tensors are not supported as answers")
            if t.layout != torch.strided:
                t = t.to_dense()
            if t.device.type != "cpu":
                t = t.cpu()
            return {"$tensor": {"shape": list(t.shape),
                                "dtype": str(t.dtype).removeprefix("torch."),
                                "data": t.reshape(-1).tolist()}}
        if isinstance(value, (tuple, list)):
            return [encode(v) for v in value]
        if isinstance(value, dict):
            return {str(k): encode(v) for k, v in value.items()}
        return value

    return decode, decode_list, encode


def _identity(value):
    return value


def _register(core, torch, payload: dict) -> None:
    """Point every Tensor-typed parameter at the decoder and every declared
    return type at the encoder, for function and class problems alike."""
    decode, decode_list, encode = _make_codec(torch)
    param_types, return_types = set(), set()

    def params_of(lst):
        for p in lst or []:
            if isinstance(p, dict):
                param_types.add(p.get("type") or "")

    params_of(payload.get("params"))
    return_types.add(payload.get("return_type") or "")
    for m in payload.get("class_methods") or []:
        params_of(m.get("params"))
        return_types.add((m.get("returns") or {}).get("type") or "")

    for typ in param_types | return_types:
        if typ in core._CODECS:  # never shadow a core type (TreeNode, ...)
            continue
        dec = {"Tensor": decode, "Tensor[]": decode_list}.get(typ, _identity)
        enc = encode if typ in return_types else None
        if typ in _TENSOR_TYPES or enc is not None:
            # (class to inject, decoder, encoder). Injecting the torch module
            # puts `torch` in the solution's globals, as `TreeNode` is for trees.
            core._CODECS[typ] = (torch, dec, enc)


def _fail_all(core, workdir: str, payload: dict, message: str) -> None:
    core._write_results(workdir, [
        {"name": t["name"], "status": "error", "error": message,
         "time_ms": 0, "stdout": ""} for t in payload.get("tests", [])])


def main() -> None:
    workdir = sys.argv[1]
    core = _load_core(workdir)
    with open(os.path.join(workdir, "payload.json"), encoding="utf-8") as f:
        payload = json.load(f)
    try:
        import torch
    except BaseException:  # noqa: BLE001 - report it per test, never die silently
        _fail_all(core, workdir, payload,
                  "PyTorch failed to import in the sandbox:\n" + traceback.format_exc()[-1500:])
        return
    torch.set_num_threads(1)
    with contextlib.suppress(RuntimeError):  # already initialised — harmless
        torch.set_num_interop_threads(1)
    # Nothing a test checks may depend on torch's RNG (the canonical and the
    # submission run in different processes), but a fixed seed keeps a stray
    # use reproducible from run to run.
    torch.manual_seed(0)
    _register(core, torch, payload)
    core.main()


if __name__ == "__main__":
    main()
