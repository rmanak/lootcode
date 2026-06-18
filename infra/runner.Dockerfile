# Sandbox image for the `docker` executor backend (EXECUTOR_BACKEND=docker).
# The harness is mounted in at runtime; this image only provides Python.
# Build:  docker build -f infra/runner.Dockerfile -t lootcode-runner .
#
# The executor runs containers with:
#   --network none --cap-drop ALL --security-opt no-new-privileges
#   --read-only --memory/--cpus/--pids-limit --user 65534:65534 (nobody)
FROM python:3.12-slim

WORKDIR /sandbox
USER 65534:65534
CMD ["python3"]
