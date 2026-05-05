from email.message import EmailMessage
import smtplib

from app.config import (
    SMTP_ENABLED,
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_USE_TLS,
)


def print_email_preview(to_email: str, subject: str, content: str) -> None:
    print("EMAIL SIMULE")
    print("A :", to_email)
    print("Sujet :", subject)
    print("Message :", content)
    print("-" * 40)


def build_email_message(to_email: str, subject: str, content: str) -> EmailMessage:
    message = EmailMessage()
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(content)
    return message


def send_email(to_email: str, subject: str, content: str) -> bool:
    if not SMTP_ENABLED:
        print_email_preview(to_email, subject, content)
        return False

    message = build_email_message(to_email, subject, content)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            if SMTP_USE_TLS:
                smtp.starttls()

            if SMTP_USERNAME:
                smtp.login(SMTP_USERNAME, SMTP_PASSWORD)

            smtp.send_message(message)
    except OSError as exc:
        print(f"EMAIL NON ENVOYE : {exc}")
        return False

    return True
