from flask import Blueprint, jsonify, request

from services.auth_service import get_supabase, get_current_user


auth_bp = Blueprint("auth", __name__, url_prefix="/api/users")


@auth_bp.post("/sync")
def sync_user():
    """Create or update the application user after Google login."""
    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    user_metadata = user.user_metadata or {}

    row = {
        "id": str(user.id),
        "email": user.email,
        "name": user_metadata.get("full_name") or user_metadata.get("name") or user.email,
        "avatar_url": user_metadata.get("avatar_url") or user_metadata.get("picture"),
    }

    get_supabase().table("users").upsert(row, on_conflict="id").execute()

    return jsonify(row), 200


@auth_bp.get("")
def list_users():
    """Return users so the creator can choose an assignee."""
    current_user = get_current_user()

    if not current_user:
        return jsonify({"error": "Unauthorized"}), 401

    result = (
        get_supabase()
        .table("users")
        .select("id,name,email,avatar_url")
        .neq("id", str(current_user.id))
        .order("name")
        .execute()
    )

    return jsonify(result.data), 200
