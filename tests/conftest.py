from collections.abc import Generator
from os import getenv

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import get_db
from app.main import app


TEST_DATABASE_URL = getenv(
    "LEAPSCOPE_TEST_DATABASE_URL",
    "postgresql+psycopg://leapscope_test:test-password@127.0.0.1:5433/leapscope_test?connect_timeout=3",
)

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestSessionFactory = sessionmaker(
    bind=test_engine,
    class_=Session,
    expire_on_commit=False,
)


def override_get_db() -> Generator[Session, None, None]:
    with TestSessionFactory() as session:
        yield session


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
        test_engine.dispose()
    