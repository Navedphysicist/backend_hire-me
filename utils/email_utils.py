from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from core.config import settings
from pathlib import Path

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates"
)

def generate_otp(length: int = 6) -> str:
    import random, string
    return ''.join(random.choices(string.digits, k=length))

async def send_verification_email(email: str, otp: str):
    try:
        message = MessageSchema(
            subject="Verify your email address",
            recipients=[email],
            template_body={"otp": otp},
            subtype="html"
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verification_email.html")
        return True

    except Exception as e:
        print(f"Unexpected error while sending email: {e}")
        return False