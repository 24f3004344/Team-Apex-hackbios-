import os

# Pure standard library .env loader (100% dependency-free for cloud deployments)
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    try:
        with open(_env_path, "r", encoding="utf-8") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip().strip('"').strip("'"))
    except Exception:
        pass


from flask import Flask, session
from db import init_db, close_db, get_db, DATABASE
from auth_middleware import login_required
from routes import register_routes

# Initialize Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "swasthya-setu-secure-secret-key-2026")


# Automatically close database connection when the request ends
app.teardown_appcontext(close_db)

# Initialize database schema and demo seed data upon launch
init_db()


# =====================================================================
# GLOBAL TEMPLATE CONTEXT
# =====================================================================

@app.context_processor
def inject_global_data():
    """Inject current_user into all templates (uses per-request DB)."""
    current_user = None
    if "user_id" in session:
        db = get_db()
        current_user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    return dict(current_user=current_user)


# =====================================================================
# MODULAR BLUEPRINT ROUTES REGISTRATION
# =====================================================================

register_routes(app)


# =====================================================================
# APPLICATION ENTRYPOINT
# =====================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting AarogyaSahay Health Grid on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True)
