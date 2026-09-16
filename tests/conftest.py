from collections.abc import Generator
from os import getenv

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

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


@pytest.fixture

def db_session() -> Generator[Session, None, None]:
    with test_engine.connect() as connection:
        transaction = connection.begin() # outer transaction (a big transaction encompassing every database action in a test) makes sure changes get reverted after rollback

        try:
            with Session(
                bind=connection,
                expire_on_commit=False,
                join_transaction_mode="create_savepoint"
            ) as session:
                yield session
        finally:
            transaction.rollback()


@pytest.fixture

def client(
    db_session: Session
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)