import time
from datetime import timedelta

import pytest
from faker import Faker
from fastapi import HTTPException
from pydantic.error_wrappers import ValidationError

from ...crud.crud_users import (
    control_user_activity,
    create_new_user,
    delete_user,
    get_current_active_user,
    get_current_user,
    get_user_by_email,
    is_active,
    update_user_language,
    update_user_timezone,
    user_authentication,
    validate_user_timezone,
)
from ...models.user import User as UserModel
from ...schemas.user import UserCreate


class TestCrudUser:
    @property
    def generate_random_email(self):
        fake = Faker()
        return fake.email()

    @property
    def generate_random_password(self):
        fake = Faker()
        return fake.password(
            length=12, special_chars=True, digits=True, upper_case=True, lower_case=True
        )

    @property
    def generate_random_full_name(self):
        fake = Faker()
        return fake.name()

    @pytest.fixture(autouse=True)
    def setup(
        self,
        override_get_db,
        register_test_user,
        register_test_user_with_timezone,
        retrieve_test_user_token_headers,
    ):
        self.token = retrieve_test_user_token_headers[1]
        self.db = override_get_db
        self.user = register_test_user
        self.user_with_timezone = register_test_user_with_timezone
        self.random_email = self.generate_random_email
        self.random_password = self.generate_random_password
        self.random_full_name = self.generate_random_full_name

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "timezone, expected",
        [
            ("Europe/Warsaw", True),
            ("UTC", True),
            ("UTC+1", False),
            ("America/New York", True),
            (None, False),
            (5, False),
            ("", False),
        ],
    )
    def test_validate_user_timezone(self, timezone: str, expected: bool):
        assert validate_user_timezone(timezone) == expected

    @pytest.mark.unit
    def test_valid_get_user_by_email(self):
        user = get_user_by_email(self.db, self.user.email)
        assert user.email == self.user.email

    @pytest.mark.unit
    @pytest.mark.parametrize("email", [None, 5, "", "invalid_email"])
    def test_invalid_get_user_by_email(self, email: str):
        user = get_user_by_email(self.db, email)
        assert user is None

    @pytest.mark.unit
    def test_user_authentication_valid(self):
        user = user_authentication(self.db, self.user.email, "XS#1sdf111#!")
        assert user is not None

    @pytest.mark.unit
    def test_user_authentication_invalid(self):
        user = user_authentication(self.db, self.random_email, self.random_password)
        assert user is None

    @pytest.mark.unit
    def test_user_authentication_invalid_password(self):
        user = user_authentication(
            self.db, self.user.email, self.generate_random_password
        )
        assert user is None

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "email, password, expected",
        [
            ("", "XS#1sdf111#!", False),
            ("test1@example.com", "", False),
            ("", "", False),
        ],
    )
    def test_user_authentication_parameter_not_provided(
        self, email, password, expected
    ):
        user = user_authentication(self.db, email, password)
        assert user is None

    @pytest.mark.unit
    @pytest.mark.parametrize("language", ["PL", "ENG"])
    def test_update_user_language_valid(self, language: str):
        user = update_user_language(self.db, self.user, language)
        assert user.language == language

    @pytest.mark.unit
    @pytest.mark.parametrize("language", ["GR", None])
    def test_update_user_language_invalid(self, language: str):
        with pytest.raises(ValueError) as exception_info:
            update_user_language(self.db, self.user, language)
        assert f"Language {language} is not supported" in str(exception_info.value)

    @pytest.mark.integration
    @pytest.mark.parametrize("timezone", ["Europe/Warsaw", "UTC", "America/New York"])
    def test_integration_update_user_timezone_valid(self, timezone: str):
        user = update_user_timezone(self.db, self.user, timezone)
        assert user.timezone == timezone

    @pytest.mark.integration
    @pytest.mark.parametrize("timezone", ["UTC+1", None, 5, ""])
    def test_integration_update_user_timezone_invalid_timezone(self, timezone: str):
        with pytest.raises(HTTPException) as exception_info:
            update_user_timezone(self.db, self.user, timezone)
        assert "User provide invalid timezone" in str(exception_info.value)

    @pytest.mark.integration
    def test_integration_update_user_timezone_invalid_user(self):
        with pytest.raises(HTTPException) as exception_info:
            update_user_timezone(self.db, None, "Europe/Warsaw")
        assert "User not correctly provided" in str(exception_info.value)

    @pytest.mark.integration
    def test_integration_update_user_timezone_without_updated_timezone(self):
        with pytest.raises(HTTPException):
            update_user_timezone(self.db, self.user_with_timezone, "None")
        assert self.user_with_timezone.timezone == "Europe/Warsaw"

    @pytest.mark.unit
    def test_user_is_not_active(self):
        control_user_activity(self.db, self.user, state=False)
        assert is_active(self.user) is False

    @pytest.mark.integration
    def test_integration_user_is_active_invalid(self):
        with pytest.raises(HTTPException) as exception_info:
            control_user_activity(self.db, None, state=True)
        assert "User not correctly provided" in str(exception_info.value)

    @pytest.mark.integration
    def test_integration_user_is_active(self):
        user = control_user_activity(self.db, self.user, state=True)
        assert is_active(user) is True

    @pytest.mark.integration
    def test_user_create_valid(self):
        user = UserCreate(
            full_name=self.random_full_name,
            email=self.random_email,
            password=self.random_password,
        )
        created_user = create_new_user(self.db, user)
        assert created_user is not None
        assert isinstance(created_user, UserModel) is True

    @pytest.mark.integration
    def test_user_create_invalid_not_provide_parameters(self):
        with pytest.raises(ValidationError) as exception_info:
            UserCreate(full_name=self.random_full_name, email=self.random_email)
        assert "value_error.missing" in str(exception_info.value)
        with pytest.raises(HTTPException) as user_exception_info:
            create_new_user(self.db, None)
        assert "User need to provide necessary data" in str(user_exception_info.value)

    @pytest.mark.integration
    def test_user_create_invalid_password(self):
        with pytest.raises(ValidationError) as exception_info:
            UserCreate(
                full_name=self.random_full_name,
                email=self.random_email,
                password="hardpassword123",
            )
        assert "string does not match regex" in str(exception_info.value)

    @pytest.mark.integration
    def test_user_create_invalid_email(self):
        with pytest.raises(ValidationError) as exception_info:
            UserCreate(
                full_name=self.random_full_name,
                email="email",
                password=self.random_password,
            )
        assert "value is not a valid email address" in str(exception_info.value)

    @pytest.mark.integration
    def test_get_current_user_valid(self):
        user = get_current_user(self.token, self.db)
        assert user is not None

    @pytest.mark.integration
    def test_get_current_user_token_expired(self, monkeypatch):
        from ...core.security import create_access_token
        from ...core.settings import settings

        monkeypatch.setattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 1)
        token = create_access_token(
            subject=self.user.email,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        time.sleep(120)
        with pytest.raises(HTTPException) as exception_info:
            get_current_user(token, self.db)
        assert "Token has expired" in str(exception_info.value.detail)

    @pytest.mark.integration
    def test_get_current_user_invalid_user(self):
        from ...core.security import create_access_token

        token = create_access_token(subject=self.random_email)
        with pytest.raises(HTTPException) as exception_info:
            get_current_user(token, self.db)
        assert "Could not validate credentials" in str(exception_info.value.detail)

    @pytest.mark.integration
    def test_get_current_user_invalid_token(self):
        with pytest.raises(HTTPException) as exception_info:
            get_current_user("invalid_token", self.db)
        assert "Could not validate credentials" in str(exception_info.value.detail)

    @pytest.mark.integration
    def test_get_current_user_token_in_blacklist(self, destroy_test_user_token):
        with pytest.raises(HTTPException) as exception_info:
            get_current_user(self.token, self.db)
        assert destroy_test_user_token.message == "Token destroyed successfully"
        assert "Token is invalid or has been invalidated (logged out)." in str(
            exception_info.value.detail
        )

    @pytest.mark.unit
    def test_user_delete_valid(self):
        message = delete_user(self.db, self.user)
        assert message == {"message": "User deleted successfully"}

    @pytest.mark.unit
    def test_user_delete_invalid(self):
        with pytest.raises(HTTPException) as exception_info:
            delete_user(self.db, None)
        assert "Cannot delete user, which is not correctly provided" in str(
            exception_info.value
        )

    @pytest.mark.unit
    def test_get_current_active_user(self):
        user = get_current_active_user(self.user)
        assert user is not None
        assert user.is_active is True

    @pytest.mark.unit
    def test_get_current_active_user_invalid(self):
        control_user_activity(self.db, self.user, state=False)
        with pytest.raises(HTTPException) as exception_info:
            get_current_active_user(self.user)
        assert "Inactive user" in str(exception_info.value.detail)
