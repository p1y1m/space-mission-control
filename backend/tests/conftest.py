import os
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_mission_control.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough")

import pytest
from fastapi.testclient import TestClient
from app.database import engine
from app.main import app, attempts
from app.models import Base


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    attempts.clear()
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def register(client, email="pilot@example.com"):
    response = client.post("/api/v1/auth/register", json={
        "email": email, "display_name": "Mission Pilot", "password": "strong-password-123"
    })
    assert response.status_code == 201
    return response


@pytest.fixture
def auth_client(client):
    register(client)
    csrf = client.cookies.get("smc_csrf")
    client.headers["X-CSRF-Token"] = csrf
    return client
