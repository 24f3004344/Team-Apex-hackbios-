import os
from flask import Flask, session
from models import close_db, init_db
from models import user as user_model
from controllers import register_routes


def create_app():
    """Application factory: models -> controllers wiring with explicit view folders."""
    app = Flask(__name__, template_folder="views/templates", static_folder="views/static")
    app.secret_key = os.environ.get("SECRET_KEY", "swasthya-setu-secure-secret-key-2026")

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
        return dict(current_user=current_user)

    register_routes(app)
    return app


app = create_app()


# =====================================================================
# APPLICATION ENTRYPOINT
# =====================================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    print(f"Starting AarogyaSahay Health Grid on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)
