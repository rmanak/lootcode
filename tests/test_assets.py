"""Tests for the problem-figure serving route (see docs/problem-images.md).

The route must serve only a problem's own assets/ dir, only image types, and must
never let a request escape into solution/ or tests/.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # runs startup (init_db + seed from content/)
        yield c


def test_serves_problem_figure(client):
    r = client.get("/problems/rotate-image/assets/example-1.svg")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/svg+xml")
    assert "<svg" in r.text


def test_figure_is_referenced_in_statement(client):
    # The statement should embed the figure so it actually renders on the page.
    r = client.get("/problems/spiral-matrix")
    assert r.status_code == 200
    assert "/problems/spiral-matrix/assets/example-1.svg" in r.text


def test_missing_asset_404(client):
    assert client.get("/problems/rotate-image/assets/nope.svg").status_code == 404


def test_non_image_extension_rejected(client):
    # solution.py / cases.json must never be reachable through this route.
    assert client.get("/problems/rotate-image/assets/solution.py").status_code == 404
    assert client.get("/problems/rotate-image/assets/cases.json").status_code == 404


@pytest.mark.parametrize("path", [
    "/problems/rotate-image/assets/..%2fmeta.json",
    "/problems/rotate-image/assets/..%2f..%2fmeta.json",
    "/problems/rotate-image/assets/%2e%2e%2fsolution%2fsolution.py",
])
def test_path_traversal_rejected(client, path):
    r = client.get(path)
    assert r.status_code == 404
    assert "def " not in r.text  # never leaked source


def test_no_assets_dir_is_404(client):
    # A problem without figures (two-sum) has no assets dir -> clean 404.
    assert client.get("/problems/two-sum/assets/example-1.svg").status_code == 404
