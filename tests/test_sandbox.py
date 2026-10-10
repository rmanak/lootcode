"""The shared sandbox primitive (`app/executor/sandbox.py`).

Covers the parts every harness depends on and no problem-level test would
notice: which backend actually runs, that a run directory cannot be escaped,
and that the process cap leaves room to work in.
"""
from __future__ import annotations

import glob
import os
import shutil
import stat
import subprocess
import tempfile
import time
import uuid

import pytest

from app.config import settings
from app.executor import sandbox
from app.executor.base import Limits

HELLO_HARNESS = """
import json, os, sys
workdir = sys.argv[1]
with open(os.path.join(workdir, "payload.json")) as fh:
    payload = json.load(fh)
with open(os.path.join(workdir, "result.json"), "w") as fh:
    json.dump({"results": [{"name": payload["greeting"], "status": "ok"}]}, fh)
"""


def _docker_ready() -> bool:
    if shutil.which("docker") is None:
        return False
    probe = subprocess.run(["docker", "image", "inspect", settings.DOCKER_IMAGE],
                           capture_output=True, check=False)
    return probe.returncode == 0


@pytest.fixture
def hello_harness(tmp_path):
    path = tmp_path / "hello_harness.py"
    path.write_text(HELLO_HARNESS, encoding="utf-8")
    return str(path)


@pytest.mark.slow
def test_a_harness_runs_and_its_results_come_back(hello_harness):
    data, timed_out = sandbox.run_harness(
        harness_path=hello_harness, files={"solution.py": "x = 1\n"},
        payload={"greeting": "hi"}, limits=Limits(), overall_s=20)
    assert not timed_out
    assert data == {"results": [{"name": "hi", "status": "ok"}]}


def test_an_input_path_cannot_escape_the_run_directory(hello_harness):
    """Names come from the app today; this keeps that from being load-bearing."""
    for bad in ("../escape.py", "/tmp/escape.py", "nested/../../escape.py"):
        with pytest.raises(ValueError, match="escapes the run directory"):
            sandbox.run_harness(harness_path=hello_harness, files={bad: "boom"},
                                payload={"greeting": "hi"}, limits=Limits(),
                                overall_s=5)


SYMLINK_HARNESS = """
import os, sys
os.symlink("/dev/zero", os.path.join(sys.argv[1], "result.json"))
"""

FIFO_HARNESS = """
import os, sys
os.mkfifo(os.path.join(sys.argv[1], "result.json"))
"""


@pytest.mark.slow
@pytest.mark.parametrize("source,what", [(SYMLINK_HARNESS, "symlink"),
                                         (FIFO_HARNESS, "fifo")])
def test_a_planted_result_file_cannot_hang_or_exhaust_the_server(tmp_path, source,
                                                                 what):
    """The run directory belongs to untrusted code, so reading back from it is
    the one place the *server* is exposed.

    A `result.json` symlinked to /dev/zero read until the host process was
    OOM-killed — with the database mid-write, that is the corruption scenario
    docs/database.md exists for — and a fifo blocked the request thread
    forever, leaking the run directory with it.
    """
    harness = tmp_path / f"{what}_harness.py"
    harness.write_text(source, encoding="utf-8")

    started = time.monotonic()
    data, _timed_out = sandbox.run_harness(
        harness_path=str(harness), files={}, payload={}, limits=Limits(),
        overall_s=20)
    assert data is None, f"a {what} must not be read as a result"
    assert time.monotonic() - started < 20, "reading it back must not block"


def test_a_result_file_larger_than_a_result_is_ignored(tmp_path):
    workdir = tmp_path / "run"
    workdir.mkdir()
    (workdir / "result.json").write_bytes(b"{" + b" " * sandbox.MAX_RESULT_BYTES)
    assert sandbox.read_results(str(workdir)) is None


@pytest.mark.slow
@pytest.mark.skipif(not _docker_ready(),
                    reason="needs docker and the lootcode-runner image")
def test_a_docker_run_leaves_nothing_behind(monkeypatch, tmp_path):
    """Guarantee 1: the sandbox is destroyed after the run.

    The container used to run as `nobody`, so a `__pycache__` it created in
    the bind-mounted run directory could not be removed by us — `rmtree`
    failed, `ignore_errors=True` hid it, and a compiled copy of the
    submission stayed in /tmp.
    """
    harness = tmp_path / "writer_harness.py"
    harness.write_text("""
import json, os, sys
workdir = sys.argv[1]
os.makedirs(os.path.join(workdir, "subdir"), exist_ok=True)
with open(os.path.join(workdir, "subdir", "left_behind.txt"), "w") as fh:
    fh.write("x")
with open(os.path.join(workdir, "result.json"), "w") as fh:
    json.dump({"results": [{"name": "t", "status": "ok"}]}, fh)
""", encoding="utf-8")

    monkeypatch.setattr(settings, "EXECUTOR_BACKEND", "docker")
    # Look only for this run's own directory. The runs root is shared with
    # every other sandbox user on the machine — `make check` runs the ICF
    # verifier alongside this suite, and a live dev server may be grading — so
    # diffing the whole root blamed this test for their in-flight runs.
    prefix = f"lc_leak_probe_{uuid.uuid4().hex}_"
    data, _ = sandbox.run_harness(harness_path=str(harness), files={}, payload={},
                                  limits=Limits(), overall_s=60, prefix=prefix)
    assert data is not None, "the container should have produced a result"
    runs_root = os.path.join(tempfile.gettempdir(), f"lootcode-runs-{os.getuid()}")
    leftovers = glob.glob(os.path.join(runs_root, prefix + "*"))
    assert not leftovers, f"run directories survived: {leftovers}"


def test_run_directories_live_where_nobody_else_can_read_them():
    """The docker backend makes the leaf world-usable; the parent is what
    stops that from publishing the submitted code to every local user."""
    workdir = sandbox.make_workdir("lc_test_")
    try:
        parent = os.path.dirname(workdir)
        mode = stat.S_IMODE(os.stat(parent).st_mode)
        assert mode == 0o700, f"{parent} is {oct(mode)}"
        assert os.stat(parent).st_uid == os.getuid()
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def test_a_timed_out_container_is_killed_not_orphaned(monkeypatch, tmp_path):
    """`docker run` timing out kills the client; the daemon keeps the
    container, and an infinite-loop submission keeps its CPU share forever."""
    killed = []

    def fake_run(cmd, **kwargs):
        if cmd[:2] == ["docker", "kill"]:
            killed.append(cmd[2])
            return subprocess.CompletedProcess(cmd, 0)
        raise subprocess.TimeoutExpired(cmd, 1)

    monkeypatch.setattr(settings, "EXECUTOR_BACKEND", "docker")
    monkeypatch.setattr(subprocess, "run", fake_run)
    harness = tmp_path / "h.py"
    harness.write_text("pass\n", encoding="utf-8")

    _data, timed_out = sandbox.run_harness(harness_path=str(harness), files={},
                                           payload={}, limits=Limits(),
                                           overall_s=1)
    assert timed_out
    assert killed and killed[0].startswith("lootcode-run-")


def test_the_process_cap_is_headroom_above_what_the_machine_is_running():
    """A flat cap counts the desktop's threads too, and a fork then fails."""
    current = sandbox._user_task_count()
    limit = sandbox.nproc_limit(slack=64)
    assert limit >= sandbox.MIN_TASK_LIMIT
    if current:
        assert limit >= current + 64 or limit == sandbox.MIN_TASK_LIMIT
        assert limit > current, "a run must be able to start at least one process"


def test_the_backend_setting_decides_where_a_harness_runs(monkeypatch,
                                                          hello_harness):
    """An operator who turned on `docker` must not silently keep the host."""
    calls = []
    monkeypatch.setattr(sandbox, "_run_harness_docker",
                        lambda *a, **k: (calls.append("docker"), ({}, False))[1])
    monkeypatch.setattr(sandbox, "_run_harness_subprocess",
                        lambda *a, **k: (calls.append("subprocess"), ({}, False))[1])

    monkeypatch.setattr(settings, "EXECUTOR_BACKEND", "docker")
    sandbox.run_harness(harness_path=hello_harness, files={}, payload={},
                        limits=Limits(), overall_s=5)
    monkeypatch.setattr(settings, "EXECUTOR_BACKEND", "subprocess")
    sandbox.run_harness(harness_path=hello_harness, files={}, payload={},
                        limits=Limits(), overall_s=5)
    assert calls == ["docker", "subprocess"]


def test_the_container_flags_are_the_documented_ones():
    cmd = sandbox.docker_command("/tmp/wd", Limits(memory_limit_mb=256),
                                 "/sandbox/harness.py", "lootcode-run-abc")
    for flag in ("--network", "none", "--cap-drop", "ALL", "--read-only",
                 "--security-opt", "no-new-privileges", "--pids-limit"):
        assert flag in cmd
    # Non-root, and specifically *our* uid: a bind mount has no uid mapping,
    # so anything the container creates as another user cannot be deleted
    # afterwards and the run directory outlives the run.
    assert "--user" in cmd and f"{os.getuid()}:{os.getgid()}" in cmd
    assert os.getuid() != 0, "these tests assume a non-root developer account"
    # The same file-size ceiling the subprocess backend gets from RLIMIT_FSIZE;
    # without it the bind mount is an unbounded write target on the host.
    assert "--ulimit" in cmd
    assert any(flag.startswith("fsize=") for flag in cmd)
    # Named, so a timed-out run can be killed rather than left burning CPU.
    assert "--name" in cmd and "lootcode-run-abc" in cmd
    assert cmd[-3:] == ["-I", "/sandbox/harness.py", "/sandbox"]


@pytest.mark.slow
@pytest.mark.skipif(not _docker_ready(),
                    reason="needs docker and the lootcode-runner image")
def test_the_docker_backend_really_runs_and_really_has_no_network(monkeypatch,
                                                                  hello_harness):
    """Also pins the fix for a run directory the container user cannot read:
    mkdtemp makes it 0700 and the container is `nobody`."""
    monkeypatch.setattr(settings, "EXECUTOR_BACKEND", "docker")
    data, timed_out = sandbox.run_harness(
        harness_path=hello_harness, files={}, payload={"greeting": "hi"},
        limits=Limits(), overall_s=60)
    assert not timed_out and data == {"results": [{"name": "hi", "status": "ok"}]}

    net_harness = hello_harness.replace("hello_harness.py", "net_harness.py")
    with open(net_harness, "w", encoding="utf-8") as fh:
        fh.write("""
import json, os, socket, sys
workdir = sys.argv[1]
socket.setdefaulttimeout(5)
try:
    socket.create_connection(("1.1.1.1", 53))
    reachable = True
except OSError:
    reachable = False
with open(os.path.join(workdir, "result.json"), "w") as fh:
    json.dump({"results": [{"name": "net", "status": str(reachable)}]}, fh)
""")
    data, _ = sandbox.run_harness(harness_path=net_harness, files={}, payload={},
                                  limits=Limits(), overall_s=60)
    assert data["results"][0]["status"] == "False", "the container had network"
