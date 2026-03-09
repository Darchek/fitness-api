"""Basic smoke tests — no DB required."""
import os
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("SECRET_KEY", "test-secret-key")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_app_starts():
    assert app is not None

def test_docs_available():
    response = client.get("/docs")
    assert response.status_code == 200
