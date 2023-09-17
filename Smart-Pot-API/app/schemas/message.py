from pydantic import BaseModel

from app.schemas.mail import EmailResponse


class Message(BaseModel):
    message: str


class EmailMessage(BaseModel):
    detail: str
    emailResponse: EmailResponse
