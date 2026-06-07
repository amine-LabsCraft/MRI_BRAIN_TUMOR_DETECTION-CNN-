"""
End-to-end tests for the BrainScan FastAPI backend.

Run:
    pytest tests/ -v

These tests load the real ResNet50 checkpoint (~98.5 MB) once via the
`client` fixture, then exercise every endpoint.
"""
from __future__ import annotations


# ─── /health ───────────────────────────────────────────────────────────────────
def test_health_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["model"] == "ResNet50"
    assert data["accuracy"] == "98.96%"
    assert data["classes"] == ["Glioma", "Meningioma", "No Tumor", "Pituitary"]


# ─── /predict ──────────────────────────────────────────────────────────────────
def test_predict_jpeg(client, fake_jpeg_bytes):
    r = client.post(
        "/predict",
        files={"file": ("test.jpg", fake_jpeg_bytes, "image/jpeg")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["predicted_class"] in ["Glioma", "Meningioma", "No Tumor", "Pituitary"]
    assert 0 <= data["confidence"] <= 1
    assert sum(data["probabilities"].values()) == pytest_almost_one()
    assert data["original_image"]
    assert data["inference_time_ms"] > 0


def test_predict_png(client, fake_png_bytes):
    r = client.post(
        "/predict",
        files={"file": ("test.png", fake_png_bytes, "image/png")},
    )
    assert r.status_code == 200


def test_predict_invalid_format(client):
    r = client.post(
        "/predict",
        files={"file": ("test.txt", b"not an image", "text/plain")},
    )
    assert r.status_code == 400


def test_predict_cache_hit(client, fake_jpeg_bytes):
    """Same image submitted twice → 2nd call should set from_cache=True."""
    r1 = client.post(
        "/predict",
        files={"file": ("a.jpg", fake_jpeg_bytes, "image/jpeg")},
    )
    r2 = client.post(
        "/predict",
        files={"file": ("a.jpg", fake_jpeg_bytes, "image/jpeg")},
    )
    assert r1.status_code == r2.status_code == 200
    assert r2.json()["from_cache"] is True


# ─── /random ──────────────────────────────────────────────────────────────────
def test_random_returns_prediction(client):
    r = client.get("/random")
    assert r.status_code == 200
    data = r.json()
    assert "predicted_class" in data
    assert "true_class" in data
    assert "gradcam_overlay" in data


# ─── /explain ─────────────────────────────────────────────────────────────────
def test_explain_glioma(client):
    r = client.get("/explain/glioma")
    assert r.status_code == 200
    data = r.json()
    assert "description" in data and "urgency" in data


def test_explain_no_tumor(client):
    r = client.get("/explain/no_tumor")
    assert r.status_code == 200


def test_explain_unknown_class(client):
    r = client.get("/explain/unknown_xyz")
    assert r.status_code == 404


# ─── /sample ──────────────────────────────────────────────────────────────────
def test_sample_pituitary(client):
    r = client.get("/sample/pituitary")
    assert r.status_code == 200
    data = r.json()
    assert data["class"] == "Pituitary"
    assert data["image_base64"]


def test_sample_unknown_class(client):
    r = client.get("/sample/xyz")
    assert r.status_code == 404


# ─── /stats ───────────────────────────────────────────────────────────────────
def test_stats(client):
    r = client.get("/stats")
    assert r.status_code == 200
    data = r.json()
    assert "total_predictions" in data
    assert "class_distribution" in data


# ─── /batch ───────────────────────────────────────────────────────────────────
def test_batch(client, fake_jpeg_bytes):
    files = [
        ("files", ("a.jpg", fake_jpeg_bytes, "image/jpeg")),
        ("files", ("b.jpg", fake_jpeg_bytes, "image/jpeg")),
    ]
    r = client.post("/batch", files=files)
    assert r.status_code == 200
    data = r.json()
    assert data["count"] == 2
    assert len(data["results"]) == 2


# ─── helpers ──────────────────────────────────────────────────────────────────
def pytest_almost_one(tol: float = 0.01) -> float:
    """Pytest helper to compare ~1.0 with tolerance."""
    import pytest
    return pytest.approx(1.0, abs=tol)
