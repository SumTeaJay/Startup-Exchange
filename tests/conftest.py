import os

os.environ["DATABASE_URL"] = "sqlite:///./test_startup_exchange.db"
os.environ["JWT_SECRET"] = "test-secret"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app
from app.security import hash_password
from app.db import SessionLocal
from app.models import User


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        db.add_all([
            User(email="a@example.com", password_hash=hash_password("password123"), name="Author"),
            User(email="b@example.com", password_hash=hash_password("password123"), name="Applicant"),
        ])
        db.commit()
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def login(client, email):
    response = client.post("/api/auth/login", json={"email": email, "password": "password123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
