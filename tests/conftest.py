"""
Pytest configuration & shared fixtures.

The API tests use FastAPI's TestClient which spins up the app in-process — no
external uvicorn needed, no port conflicts.
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

import pytest
from PIL import Image
import numpy as np

# Make project root importable
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Disable rate limiting in tests
os.environ.setdefault("BRAINSCAN_DISABLE_RATELIMIT", "1")
os.environ.setdefault("BRAINSCAN_API_KEY", "")  # no auth in tests


@pytest.fixture(scope="session")
def client():
    """FastAPI TestClient (spins up app in-process, loads model once)."""
    from fastapi.testclient import TestClient
    from api.app import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def fake_jpeg_bytes() -> bytes:
    """Return a tiny in-memory JPEG (224x224, RGB, gray pattern)."""
    arr = (np.random.rand(224, 224, 3) * 255).astype("uint8")
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def fake_png_bytes() -> bytes:
    arr = (np.random.rand(64, 64, 3) * 255).astype("uint8")
    img = Image.fromarray(arr)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
