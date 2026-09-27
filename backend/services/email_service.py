import base64
import json
import os
from email.message import EmailMessage

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]


def get_gmail_credentials():
    # Production: token stored in Render environment variable
    token_json = os.getenv("GMAIL_TOKEN_JSON")

    if token_json:
        token_data = json.loads(token_json)

        creds = Credentials.from_authorized_user_info(
            token_data,
            SCOPES
        )

    else:
        # Local development: use token.json
        base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )

        token_path = os.path.join(
            base_dir,
            "token.json"
        )

        creds = Credentials.from_authorized_user_file(
            token_path,
            SCOPES
        )

    # Refresh expired access token
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds


def get_gmail_service():
    credentials = get_gmail_credentials()

    return build(
        "gmail",
        "v1",
        credentials=credentials
    )


def send_email(to_email, subject, body):
    try:
        service = get_gmail_service()

        message = EmailMessage()

        message["To"] = to_email
        message["Subject"] = subject

        message.set_content(body)

        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        result = (
            service.users()
            .messages()
            .send(
                userId="me",
                body={
                    "raw": encoded_message
                }
            )
            .execute()
        )

        print("===================================")
        print("GMAIL API EMAIL SENT")
        print("TO:", to_email)
        print("MESSAGE ID:", result.get("id"))
        print("===================================")

        return True

    except Exception as error:
        print("===================================")
        print("GMAIL API EMAIL ERROR")
        print(repr(error))
        print("===================================")

        return False