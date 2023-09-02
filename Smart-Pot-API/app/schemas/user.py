from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from app.schemas.plant import Plant

""" Pydantic models to validate data about Users"""


class UserBase(BaseModel):
    """
    Base class for User Pydantic model
    """

    full_name: str
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = False


class UserCreate(BaseModel):
    """
    User which we're putting as parameter creating new one.
    """

    full_name: str
    email: EmailStr = Field(..., description="Email must be provided")
    password: str = Field(
        ..., description="Password must be provided"
    )  # ... in field means that this field is required.


class UserUpdate(UserBase):
    password: str = Field(
        ..., description="Password must be provided"
    )  # ... in field means that this field is required.


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
