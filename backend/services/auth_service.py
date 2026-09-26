from flask import request
from supabase import create_client

from config import SUPABASE_SECRET_KEY, SUPABASE_URL


_supabase = None


def get_supabase():
    """Create the Supabase client once and reuse it."""
    global _supabase

    if _supabase is None:
        if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
            raise RuntimeError("Supabase environment variables are missing")

        _supabase = create_client(
            SUPABASE_URL,
            SUPABASE_SECRET_KEY
        )

    return _supabase


def get_current_user():
    """Check the access token sent by the frontend."""
    auth_header = request.headers.get("Authorization", "")

    # We expect: Authorization: Bearer <token>
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "", 1).strip()

    if not token:
        return None

    try:
        # Supabase checks whether this token belongs to a valid user.
        response = get_supabase().auth.get_user(token)
        return response.user

    except Exception as error:
        print(f"Auth error: {error}")
        return None