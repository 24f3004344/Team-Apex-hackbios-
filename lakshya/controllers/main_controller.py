from flask import Blueprint, render_template, request, session
from models import user as user_model, referral, medicine, teleconsult, high_risk_case
from middleware.auth_middleware import login_required

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
    user = user_model.get_by_id(session["user_id"])
    referrals = referral.list_all()
    medicines = medicine.list_all()
    teleconsults = teleconsult.list_queue()
    high_risk_cases = high_risk_case.list_all()

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

