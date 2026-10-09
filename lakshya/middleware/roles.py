from functools import wraps
from flask import flash, jsonify, redirect, request, session, url_for

#: Staff roles allowed to mutate clinical/operational records.
STAFF = ("frontline", "doctor", "admin")


def require_roles(*allowed):
    """Allow only logged-in users whose session role is in `allowed`.

    Must be stacked UNDER @login_required. API paths get JSON 403,
    page routes get a flash + redirect to dashboard.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if session.get("user_role") not in allowed:
                if request.path.startswith("/api/"):
                    return jsonify({"success": False, "error": "Forbidden for your role"}), 403
                flash("Your role cannot perform this action.", "danger")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return wrapper
    return decorator
