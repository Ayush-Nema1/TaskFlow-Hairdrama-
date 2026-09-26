from datetime import datetime, timezone

from flask import Blueprint, jsonify, request

from services.auth_service import get_supabase, get_current_user
from services.email_service import send_email


tasks_bp = Blueprint("tasks", __name__, url_prefix="/api/tasks")


def get_users_by_ids(user_ids):
    """Get a few user records in one small helper."""
    if not user_ids:
        return []

    result = (
        get_supabase()
        .table("users")
        .select("id,name,email")
        .in_("id", list(user_ids))
        .execute()
    )
    return result.data or []


@tasks_bp.get("")
def list_tasks():
    """Show tasks created by the logged-in user or assigned to them."""
    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = str(user.id)

    created = get_supabase().table("tasks").select("*").eq("created_by", user_id).order("created_at", desc=True).execute().data or []
    assigned = get_supabase().table("tasks").select("*").eq("assigned_to", user_id).order("created_at", desc=True).execute().data or []

    # Merge both lists without duplicates.
    tasks = {task["id"]: task for task in created + assigned}

    user_ids = set()
    for task in tasks.values():
        user_ids.add(task["created_by"])
        user_ids.add(task["assigned_to"])

    users = {user["id"]: user for user in get_users_by_ids(user_ids)}

    output = []
    for task in tasks.values():
        output.append({
            **task,
            "creator": users.get(task["created_by"]),
            "assignee": users.get(task["assigned_to"]),
        })

    output.sort(key=lambda item: item.get("created_at", ""), reverse=True)
    return jsonify(output), 200


@tasks_bp.post("")
def create_task():
    """Create a task and email the person who was assigned."""
    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    assigned_to = str(data.get("assigned_to", "")).strip()

    if not title:
        return jsonify({"error": "Title is required"}), 400

    if not assigned_to:
        return jsonify({"error": "Please select an assignee"}), 400

    if assigned_to == str(user.id):
        return jsonify({"error": "A task must be assigned to another user"}), 400

    assignees = get_users_by_ids({assigned_to})
    if not assignees:
        return jsonify({"error": "Assignee not found"}), 404

    assignee = assignees[0]

    task_data = {
        "title": title,
        "description": description,
        "created_by": str(user.id),
        "assigned_to": assigned_to,
        "status": "pending",
    }

    result = get_supabase().table("tasks").insert(task_data).execute()
    task = result.data[0]

    # Saving the task is more important than email delivery.
    try:
        send_email(
            assignee["email"],
            "New task assigned to you",
            f"You have a new task: {title}\n\n{description}\n",
        )
    except Exception as error:
        print(f"Email error: {error}")

    return jsonify(task), 201


@tasks_bp.patch("/<int:task_id>/complete")
def complete_task(task_id):
    """Mark an assigned task as completed and notify the creator."""
    user = get_current_user()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    task_result = (
        get_supabase()
        .table("tasks")
        .select("*")
        .eq("id", task_id)
        .maybe_single()
        .execute()
    )

    task = task_result.data
    if not task:
        return jsonify({"error": "Task not found"}), 404

    if task["assigned_to"] != str(user.id):
        return jsonify({"error": "Only the assignee can complete this task"}), 403

    if task["status"] == "completed":
        return jsonify(task), 200

    completed_at = datetime.now(timezone.utc).isoformat()

    updated = (
        get_supabase()
        .table("tasks")
        .update({"status": "completed", "completed_at": completed_at})
        .eq("id", task_id)
        .execute()
    )

    updated_task = updated.data[0]

    creators = get_users_by_ids({task["created_by"]})
    if creators:
        try:
            send_email(
                creators[0]["email"],
                "Task completed",
                f"Your task '{task['title']}' has been completed.\n",
            )
        except Exception as error:
            print(f"Email error: {error}")

    return jsonify(updated_task), 200
