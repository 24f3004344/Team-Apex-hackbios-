from flask import Blueprint, render_template, request, session
from db import get_db
from auth_middleware import login_required

main_bp = Blueprint("main", __name__)


# =====================================================================
# CORE ROUTES: LANDING, DASHBOARD, RECORDS, ANALYTICS
# =====================================================================

@main_bp.route("/")
def index():
    """Landing Page."""
    return render_template("index.html")


@main_bp.route("/dashboard")
@login_required
def dashboard():
    """Integrated Care Portal."""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    referrals = db.execute("SELECT * FROM referrals ORDER BY id DESC").fetchall()
    medicines = db.execute("SELECT * FROM medicines ORDER BY stock_status ASC, units ASC").fetchall()
    teleconsults = db.execute(
        "SELECT * FROM teleconsults ORDER BY CASE priority WHEN 'Emergency' THEN 1 WHEN 'Priority' THEN 2 ELSE 3 END, id ASC"
    ).fetchall()
    high_risk_cases = db.execute(
        "SELECT * FROM high_risk_cases ORDER BY CASE status WHEN 'Critical' THEN 1 WHEN 'Due Today' THEN 2 ELSE 3 END, id ASC"
    ).fetchall()

    return render_template(
        "dashboard.html",
        user=user,
        referrals=referrals,
        medicines=medicines,
        teleconsults=teleconsults,
        high_risk_cases=high_risk_cases,
    )


@main_bp.route("/records")
def records_page():
    """Longitudinal Patient Records / ABHA Unified Medical Journey."""
    abha_query = request.args.get("abha", "91-3321-4451-0982").strip()
    return render_template("records.html", active_abha=abha_query)


@main_bp.route("/analytics")
def analytics_page():
    """Public Health Facility Quality & Impact Dashboard."""
    return render_template("analytics.html")

