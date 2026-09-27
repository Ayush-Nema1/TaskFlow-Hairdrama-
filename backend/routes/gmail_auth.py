import os

# Allow HTTP only for local development
if os.getenv("ENVIRONMENT") != "production":
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from flask import Blueprint, redirect, request, session
from google_auth_oauthlib.flow import Flow

gmail_auth_bp = Blueprint("gmail_auth", __name__)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send"
]

CLIENT_SECRETS_FILE = "credentials.json"


def get_redirect_uri():
    if os.getenv("ENVIRONMENT") == "production":
        return "https://taskflow-hairdrama.onrender.com/oauth2callback"

    return "http://localhost:5000/oauth2callback"


@gmail_auth_bp.get("/auth/gmail")
def gmail_login():

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES
    )

    flow.redirect_uri = get_redirect_uri()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    # Save OAuth values so callback can use the SAME verifier
    session["gmail_oauth_state"] = state
    session["gmail_code_verifier"] = flow.code_verifier

    return redirect(authorization_url)


@gmail_auth_bp.get("/oauth2callback")
def gmail_callback():

    saved_state = session.get("gmail_oauth_state")
    code_verifier = session.get("gmail_code_verifier")

    if not saved_state or not code_verifier:
        return "OAuth session expired. Please start again from /auth/gmail.", 400

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=saved_state,
        code_verifier=code_verifier
    )

    flow.redirect_uri = get_redirect_uri()

    flow.fetch_token(
        authorization_response=request.url
    )

    credentials = flow.credentials

    with open("token.json", "w") as token:
        token.write(credentials.to_json())

    # Remove temporary OAuth data
    session.pop("gmail_oauth_state", None)
    session.pop("gmail_code_verifier", None)

    return "Gmail authorization successful! You can close this page."