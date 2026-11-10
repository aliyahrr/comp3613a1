from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

import app.models  # noqa: F401  # register SQLModel tables
from app import main as app_main
from app.database import get_session


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine


@pytest.fixture()
def test_session(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def isolate_uploads(monkeypatch, tmp_path):
    from app.services import volunteer_hours_service

    monkeypatch.setattr(volunteer_hours_service, "upload_dir", tmp_path / "uploads")


@pytest.fixture()
def client(engine):
    def override_get_session():
        with Session(engine) as session:
            yield session

    app_main.app.dependency_overrides[get_session] = override_get_session
    with TestClient(app_main.app) as test_client:
        yield test_client
    app_main.app.dependency_overrides.clear()
