# Sandbox image for the `docker` executor backend (EXECUTOR_BACKEND=docker).
# The harness is mounted in at runtime; this image only provides Python.
# Build:  docker build -f infra/runner.Dockerfile -t lootcode-runner .
#
# The executor runs containers with:
#   --network none --cap-drop ALL --security-opt no-new-privileges
#   --read-only --memory/--cpus/--pids-limit --user <the app's uid>
#   (see sandbox.docker_command: the host uid, so the bind mount stays deletable)
FROM python:3.12-slim

# The one third-party package a submission may import (machine-learning
# problems), pinned by the same constraints file as the app. Installed as root,
# before the switch to `nobody`, so the read-only rootfs carries it. Wheels
# only: a source build would run arbitrary build code as root.
COPY constraints.txt /tmp/constraints.txt
RUN pip install --no-cache-dir --only-binary=:all: numpy -c /tmp/constraints.txt \
    && rm /tmp/constraints.txt

WORKDIR /sandbox
USER 65534:65534
CMD ["python3"]
