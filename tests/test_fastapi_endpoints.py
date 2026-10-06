"""Unit tests for FastAPI endpoints."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "Local GitHub Repository Code Explainer API"
    assert data["status"] == "running"


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["fastapi"] is True
    assert "ollama" in data


def test_ollama_status_endpoint():
    response = client.get("/api/ollama/status")
    assert response.status_code == 200
    data = response.json()
    assert "connected" in data
    assert "model_available" in data
    assert data["model_name"] == "qwen2.5:3b"


def test_analyze_endpoint_invalid_url():
    response = client.post("/api/analyze", json={"url": "invalid-url"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False
    assert "Invalid GitHub URL format" in data["error"]
