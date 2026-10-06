from fastapi.testclient import TestClient

from backend.main import app, manager

client = TestClient(app)


def test_root() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_invalid_analyze_request() -> None:
    response = client.post("/api/analyze", json={"github_url": "https://gitlab.com/a/b"})
    assert response.status_code == 400


def test_job_not_found() -> None:
    response = client.get("/api/jobs/not-found")
    assert response.status_code == 404
