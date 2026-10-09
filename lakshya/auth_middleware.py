from functools import wraps
from flask import session, flash, redirect, url_for


def login_required(f):
    """Decorator to enforce authenticated session for protected routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access your healthcare portal.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def role_required(*allowed_roles):
    """
    Decorator to enforce Role-Based Access Control (RBAC).
    Administrators have global bypass permissions across all modules.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                flash("Please sign in to access your healthcare portal.", "warning")
                return redirect(url_for("login"))

            user_role = session.get("user_role") or session.get("role")
            if not user_role and "user_id" in session:
                from db import get_db
                u = get_db().execute("SELECT role FROM users WHERE id = ?", (session["user_id"],)).fetchone()
                if u:
                    user_role = u["role"]
                    session["user_role"] = user_role

            # Admin role has full system-wide access
            if user_role == "admin" or user_role in allowed_roles:
                return f(*args, **kwargs)

            role_titles = {
                "frontline": "Frontline Worker (ASHA/ANM)",
                "doctor": "Medical Officer / Doctor",
                "patient": "Patient / Citizen",
                "admin": "Facility Administrator"
            }
            current_title = role_titles.get(user_role, (user_role or "User").capitalize())
            flash(
                f"Access restricted: {current_title} accounts do not have permission to access this module.",
                "warning"
            )
            return redirect(url_for("dashboard"))
        return decorated_function
    return decorator
