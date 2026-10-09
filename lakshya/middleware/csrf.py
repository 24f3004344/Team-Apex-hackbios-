import secrets
from functools import wraps
from flask import flash, jsonify, redirect, request, session, url_for

FIELD = "_csrf_token"
HEADER = "X-CSRF-Token"
_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})


def get_token():
    """Session-bound CSRF token, created lazily (also works pre-login for login/register forms)."""
    tok = session.get(FIELD)
    if not tok:
        tok = secrets.token_hex(32)
        session[FIELD] = tok
    return tok


def rotate_token():
    """Issue a fresh token (call on login/register to prevent fixation)."""
    session[FIELD] = secrets.token_hex(32)
    return session[FIELD]


def _submitted():
    return request.form.get(FIELD) or request.headers.get(HEADER) or (request.get_json(silent=True) or {}).get(FIELD)


def validate():
    expected = session.get(FIELD)
    return bool(expected) and expected == _submitted()


def protect(f):
    """Reject cross-site POSTs. Safe methods (GET/HEAD/OPTIONS) pass through."""
    @wraps(f)
    def wrapper(*args, **kwargs):
        if request.method in _SAFE_METHODS:
            return f(*args, **kwargs)
        if not validate():
            if request.path.startswith("/api/"):
                return jsonify({"success": False, "error": "CSRF token missing or invalid"}), 403
            flash("Session expired. Please try again.", "warning")
            return redirect(request.referrer or url_for("index"))
        return f(*args, **kwargs)
    return wrapper
