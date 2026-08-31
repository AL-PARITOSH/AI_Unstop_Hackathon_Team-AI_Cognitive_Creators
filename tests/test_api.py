import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_root_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"

def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_visual_types_endpoint(client):
    res = client.get("/visual-types")
    assert res.status_code == 200
    data = res.json()
    assert "supported_types" in data
    assert len(data["supported_types"]) == 7

def test_examples_endpoint(client):
    res = client.get("/examples")
    assert res.status_code == 200
    data = res.json()
    assert data["total_examples"] == 8

def test_select_type_endpoint(client):
    payload = {
        "topic": "Physics",
        "concept": "Ohm's Law",
        "level": "beginner"
    }
    res = client.post("/select-type", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["primary_type"] == "formula"
    assert "diagram" in data["secondary_types"]
    assert data["confidence"] >= 0.9

def test_generate_visual_endpoint(client):
    payload = {
        "topic": "Mathematics",
        "concept": "y = x?",
        "level": "intermediate",
        "language": "English",
        "lesson_context": "Explain quadratic parabola.",
        "include_secondary": True
    }
    res = client.post("/generate-visual", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["visual_type"] == "graph"
    assert data["visual_url"] is not None
    assert "http" in data["visual_url"]
    assert "visual_data" in data
    assert len(data["secondary_visuals"]) >= 1
    assert data["secondary_visuals"][0]["visual_type"] == "formula"

def test_render_view_endpoint(client):
    # First generate a visual
    payload = {"topic": "Biology", "concept": "Photosynthesis"}
    res = client.post("/generate-visual", json=payload)
    data = res.json()
    url = data["visual_url"]
    visual_filename = url.split("/")[-1]

    # Now fetch via /visuals/{visual_id}
    viewer_res = client.get(f"/visuals/{visual_filename}")
    assert viewer_res.status_code == 200
    assert "text/html" in viewer_res.headers["content-type"]
    assert "Photosynthesis" in viewer_res.text
