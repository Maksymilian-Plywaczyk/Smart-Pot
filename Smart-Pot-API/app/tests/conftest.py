import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.core.settings import settings
from app.crud.crud_users import get_current_active_user, get_current_user
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
    trans = connection.begin()
    # bind an individual Session to the connection
    session = Session(bind=connection)

    nested = connection.begin_nested()

    @sa.event.listens_for(session, "after_transaction_end")
    def end_savepoint(session, transaction):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    yield session
    # Rollback the overall transaction, restoring the state before the test ran
    session.close()
    trans.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(override_get_db):
    app.dependency_overrides[get_db] = lambda: override_get_db
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def client_without_authentication():
    def skip_authentication():
        return None

    for dependency in [get_current_active_user, get_current_user]:
        app.dependency_overrides[dependency] = skip_authentication
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def register_test_user(override_get_db):
    from app.crud.crud_users import create_new_user
    from app.schemas.user import UserCreate

    new_user = UserCreate(
        full_name="Test User", email="test1@example.com", password="XS#1sdf111#!"
    )
    yield create_new_user(override_get_db, new_user)


@pytest.fixture(scope="function")
def retrieve_test_user_token_headers(override_get_db, register_test_user):
    from app.core.security import create_access_token
    from app.crud.crud_users import set_user_to_active

    register_test_user = set_user_to_active(override_get_db, register_test_user)
    test_user_email = register_test_user.email
    token = create_access_token(subject=test_user_email)
    headers = {"Authorization": f"Bearer {token}"}
    yield headers
