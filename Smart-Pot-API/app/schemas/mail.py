from typing import Dict

from pydantic import BaseModel, EmailStr
from pydantic.types import PositiveInt


class Email(BaseModel):
    email: EmailStr
    body: Dict[str, str]


class EmailResponse(BaseModel):
    detail: str
    HTTPStatusCode: PositiveInt
