from typing import Generator
import pytest

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.db.base_class import Base
from backend.app.core.config import settings
from backend.app.main import app
from backend.app.api.deps import get_db

SQLALCHEMY_DATABASE_URI = settings.SQLALCHEMY_DATABASE_URI.replace(
    settings.PROJECT_NAME, settings.PROJECT_NAME + "_test"
)
engine = create_engine(SQLALCHEMY_DATABASE_URI)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.drop_all(bind=engine)  # start with empty db
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def db() -> Generator:
    yield TestingSessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c
