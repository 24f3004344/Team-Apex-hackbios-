import os
import secrets
from flask import Flask, session
from models import close_db, init_db
from models import user as user_model
from controllers import register_routes
from middleware.csrf import get_token


def _get_secret_key():
    """SECRET_KEY from env in production; random per-boot fallback for local dev."""
    key = os.environ.get("SECRET_KEY")
    if not key:
        print("WARNING: SECRET_KEY not set — using random per-boot key (set SECRET_KEY env for stable sessions).")
        return secrets.token_hex(32)
    return key


def _is_debug():
    return os.environ.get("FLASK_DEBUG", "0") == "1"


def create_app():
    """Application factory: models -> controllers wiring with explicit view folders."""
    app = Flask(__name__, template_folder="views/templates", static_folder="views/static")
    app.secret_key = _get_secret_key()

    # Automatically close database connection when the request ends
    app.teardown_appcontext(close_db)

    # Initialize database schema and demo seed data upon launch
    init_db()

    @app.context_processor
    def inject_global_data():
        """Inject current_user into all templates (uses per-request DB)."""
        current_user = None
        if "user_id" in session:
            current_user = user_model.get_by_id(session["user_id"])
        return dict(current_user=current_user, csrf_token=get_token)

    register_routes(app)
    return app


app = create_app()


# =====================================================================
# APPLICATION ENTRYPOINT
# =====================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting AarogyaSahay Health Grid on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=_is_debug(), use_reloader=False)
