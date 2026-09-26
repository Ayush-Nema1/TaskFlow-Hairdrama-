import smtplib
import ssl
from email.message import EmailMessage

from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD


def send_email(to_email, subject, body):
    """Send a simple email using Gmail SMTP."""

    # We keep email optional during development.
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("Gmail is not configured. Email was skipped.")
        return False

    message = EmailMessage()
    message["From"] = GMAIL_ADDRESS
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    context = ssl.create_default_context()

    # Port 465 uses SMTP over SSL.
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD.replace(" ", ""))
        server.send_message(message)

    return True
