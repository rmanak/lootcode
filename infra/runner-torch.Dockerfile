# Sandbox image for torch-runtime problems on the `docker` executor backend
# (EXECUTOR_BACKEND=docker; problems with "runtime": "torch"). See
# docs/torch-runtime.md. The harnesses are mounted in at runtime; this image
# only provides Python + CPU-only torch + numpy.
# Build:  docker build -f infra/runner-torch.Dockerfile -t lootcode-runner-torch .
#
# Same container flags as the plain runner (sandbox.docker_command): no network,
# no capabilities, read-only rootfs, memory/cpu/pids limits, the app's uid.
FROM python:3.12-slim

# Pinned by the same file as ./.venv-torch, so both backends grade with the
# same torch. Installed as root, before the switch to `nobody`, so the
# read-only rootfs carries it. Wheels only: a source build would run arbitrary
# build code as root.
COPY requirements-torch.txt /tmp/requirements-torch.txt
RUN pip install --no-cache-dir --only-binary=:all: -r /tmp/requirements-torch.txt \
    && rm /tmp/requirements-torch.txt

WORKDIR /sandbox
USER 65534:65534
CMD ["python3"]
