from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse

from app.core.settings import settings
from app.schemas.mail import Email


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
            MAIL_SERVER="sandbox.smtp.mailtrap.io",
            MAIL_STARTTLS=False,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )

    async def send_email(self, device_id: str) -> JSONResponse:
        html = """<p>Hi this test mail, thanks for using Fastapi-mail</p> """
        message = MessageSchema(
            subject=f"Authentication token for Device: {device_id}",
            recipients=[self.email.dict().get("email")],
            body=html,
            subtype=MessageType.html,
        )

        fastapi_mail = FastMail(self.config)
        await fastapi_mail.send_message(message)
        return JSONResponse(
            {"detail": "Email successfully sent", "HTTPStatusCode": 200},
            status_code=200,
        )
