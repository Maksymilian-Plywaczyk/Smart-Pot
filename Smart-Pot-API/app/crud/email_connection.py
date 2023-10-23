from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse

from ..core.settings import settings
from ..schemas.mail import Email


class MailConnection:
    def __init__(self, email: Email):
        self.config = self.create_connection_config
        self.email = email

    @property
    def create_connection_config(self):
        return ConnectionConfig(
            MAIL_USERNAME=settings.EMAIL_USERNAME,
            MAIL_PASSWORD=settings.EMAIL_PASSWORD,
            MAIL_FROM=settings.EMAIL_ADDRESS,
            MAIL_PORT=587,
            MAIL_SERVER="live.smtp.mailtrap.io",
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            TEMPLATE_FOLDER=Path(settings.EMAIL_TEMPLATE_DIR),
        )

    async def send_email_authentication_device_token(
        self, device_id: str
    ) -> JSONResponse:
        message = MessageSchema(
            subject=f"Authentication token for Device: {device_id}",
            recipients=[self.email.dict().get("email")],
            template_body=self.email.dict().get("body"),
            subtype=MessageType.html,
        )

        fastapi_mail = FastMail(self.config)
        await fastapi_mail.send_message(message, template_name="device_token.html")
        return JSONResponse(
            {"detail": "Email successfully sent", "HTTPStatusCode": 200},
            status_code=200,
        )

    async def send_email_resetting_password(self) -> JSONResponse:
        subject = f"Password recovery for user email: {self.email.dict().get('email')}"
        message = MessageSchema(
            subject=subject,
            recipients=[self.email.dict().get("email")],
            template_body=self.email.dict().get("body"),
            subtype=MessageType.html,
        )
        fastapi_mail = FastMail(self.config)
        await fastapi_mail.send_message(message, template_name="reset_password.html")
        return JSONResponse(
            {"detail": "Email successfully sent", "HTTPStatusCode": 200},
            status_code=200,
        )
