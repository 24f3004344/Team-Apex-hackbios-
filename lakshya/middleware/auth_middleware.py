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

