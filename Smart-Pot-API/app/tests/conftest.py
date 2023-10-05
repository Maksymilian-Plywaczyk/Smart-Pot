import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.settings import settings
from app.db.base import Base
from app.main import app


def get_engine() -> Engine:
    return create_engine(settings.TEST_DATABASE_URL)


@pytest.fixture(scope="session")
def db_engine():
    engine = get_engine()
    Base.metadata.create_all(bind=engine)

    yield engine


@pytest.fixture(scope="function")
def override_get_db(db_engine):
    # connect to database
    connection = db_engine.connect()
    # begin a non-ORM transaction
    transaction = connection.begin()
    # bind an individual Session to the connection
    db = Session(bind=connection)
    yield db
    db.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[get_db] = lambda: db
    with TestClient(app) as c:
        yield c
