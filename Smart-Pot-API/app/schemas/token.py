from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    token_type: str = Field(default="bearer", description="Type of token")


class TokenPayload(BaseModel):
    email: str = None
    exp: int = None
