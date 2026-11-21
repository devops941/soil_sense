from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal, init_db
from app.core.seed import seed_database, seed_demo_data
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
        seed_demo_data(db)
    finally:
        db.close()
    yield


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as test_client:
        yield test_client
