from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from ..schemas.plant import Plant
from ..schemas.utils.languages import Languages

""" Pydantic models to validate data about Users"""

password_regex = "((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[\W]).{8,64})"


class UserBase(BaseModel):
    """
    Base class for User Pydantic model
    """

    full_name: str
    email: Optional[EmailStr] = None
    language: Optional[Languages] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = False


class UserTimezoneSet(BaseModel):
    timezone: str


class UserCreate(BaseModel):
    """
    User which we're putting as parameter creating new one.
    """

    full_name: str
    email: EmailStr = Field(..., description="Email must be provided")
    password: str = Field(
        ..., description="Password must be provided", regex=password_regex
    )  # ... in field means that this field is required.


class UserUpdate(UserBase):
    password: str = Field(
        ..., description="Password must be provided", regex=password_regex
    )  # ... in field means that this field is required.


class UserChangePassword(BaseModel):
    token: str
    new_password: str = Field(
        ..., description="User new password", regex=password_regex
    )


class UserDelete(BaseModel):
    user_token: str
    password: str


class UserDB(UserBase):
    """User model as model from database"""

    id: int
    hashed_password: str
    plants: List[Plant] = Field(default=[], description="User's plants")

    class Config:
        orm_mode = True


class User(UserDB):
    """User model for returning properties via API"""

    pass
