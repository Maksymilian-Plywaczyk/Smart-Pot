from typing import Union

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer", description="Type of token")


class RefreshToken(BaseModel):
    token: str


class ResetToken(BaseModel):
    reset_password_token: str
    token_type: str = Field(default="bearer", description="Type of token")


class TokenPayload(BaseModel):
    email: Union[str, None] = None
