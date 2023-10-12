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
def register_test_user_with_timezone(override_get_db, register_test_user):
    from app.crud.crud_users import update_user_timezone
    from app.schemas.user import UserTimezoneSet

    timezone = UserTimezoneSet(timezone="Europe/Warsaw")
    yield update_user_timezone(override_get_db, register_test_user, timezone.timezone)


@pytest.fixture(scope="function")
def retrieve_test_user_token_headers(override_get_db, register_test_user):
    from app.core.security import create_access_token
    from app.crud.crud_users import control_user_activity

    register_test_user = control_user_activity(
        override_get_db, register_test_user, state=True
    )
    test_user_email = register_test_user.email
    token = create_access_token(subject=test_user_email)
    headers = {"Authorization": f"Bearer {token}"}
    yield headers, token


@pytest.fixture(scope="function")
def destroy_test_user_token(
    override_get_db, retrieve_test_user_token_headers, register_test_user
):
    from app.core.security import destroy_access_token

    yield destroy_access_token(
        override_get_db, retrieve_test_user_token_headers[1], register_test_user
    )
