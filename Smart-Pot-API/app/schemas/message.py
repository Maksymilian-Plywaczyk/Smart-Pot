from pydantic import BaseModel

from ..schemas.mail import EmailResponse


class Message(BaseModel):
    message: str


class EmailMessage(BaseModel):
    detail: str
    emailResponse: EmailResponse
