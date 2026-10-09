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
    """Integrated Care Portal - Adaptive Role-Based Dashboard."""
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()
    if not user:
        return redirect(url_for("auth.logout"))

    role = user["role"]
    district = user["district"] or "Bilaspur"

    # Dynamic system-wide metric counts
    total_teleconsults = db.execute("SELECT COUNT(*) FROM teleconsults").fetchone()[0]
    pending_teleconsults = db.execute("SELECT COUNT(*) FROM teleconsults WHERE status != 'Completed'").fetchone()[0]
    emergency_teleconsults = db.execute("SELECT COUNT(*) FROM teleconsults WHERE priority = 'Emergency'").fetchone()[0]
    emergency_referrals = db.execute("SELECT COUNT(*) FROM referrals WHERE urgency = 'Emergency'").fetchone()[0]
    emergency_escalations = emergency_teleconsults + emergency_referrals

    active_referrals_count = db.execute("SELECT COUNT(*) FROM referrals WHERE status IN ('Initiated', 'In-Transit')").fetchone()[0]
    low_stock_count = db.execute("SELECT COUNT(*) FROM medicines WHERE stock_status IN ('Low Stock', 'Out of Stock')").fetchone()[0]
    critical_high_risk_count = db.execute("SELECT COUNT(*) FROM high_risk_cases WHERE status IN ('Critical', 'Due Today')").fetchone()[0]
    total_hospitals = db.execute("SELECT COUNT(*) FROM hospitals").fetchone()[0]

    # Shared active datasets
    referrals = db.execute("SELECT * FROM referrals ORDER BY id DESC LIMIT 6").fetchall()
    medicines = db.execute("SELECT * FROM medicines ORDER BY stock_status ASC, units ASC").fetchall()
    teleconsults = db.execute(
        "SELECT * FROM teleconsults ORDER BY CASE priority WHEN 'Emergency' THEN 1 WHEN 'Priority' THEN 2 ELSE 3 END, id ASC"
    ).fetchall()
    high_risk_cases = db.execute(
        "SELECT * FROM high_risk_cases ORDER BY CASE status WHEN 'Critical' THEN 1 WHEN 'Due Today' THEN 2 ELSE 3 END, id ASC"
    ).fetchall()

    # Role-specific tailored data
    patient_teleconsults = []
    patient_prescriptions = []
    nearby_hospitals = []

    if role == "patient":
        # Look up records matching patient's name or ABHA ID
        patient_teleconsults = db.execute(
            "SELECT * FROM teleconsults WHERE abha_id = ? OR patient_name LIKE ? ORDER BY id DESC",
            (user["abha_id"] or "", f"%{user['full_name']}%")
        ).fetchall()
        if not patient_teleconsults:
            # Fallback to recent teleconsultations so demo profile shows active continuum of care
            patient_teleconsults = db.execute("SELECT * FROM teleconsults ORDER BY id DESC LIMIT 3").fetchall()

        patient_prescriptions = [t for t in patient_teleconsults if t["prescription"]]

        nearby_hospitals = db.execute(
            "SELECT id, hospital_name, hospital_type, address, phone1 FROM hospitals WHERE district = ? ORDER BY hospital_type, hospital_name LIMIT 4",
            (district,)
        ).fetchall()

    stats = {
        "total_teleconsults": total_teleconsults,
        "pending_teleconsults": pending_teleconsults,
        "emergency_escalations": emergency_escalations,
        "active_referrals": active_referrals_count,
        "low_stock_medicines": low_stock_count,
        "critical_high_risk": critical_high_risk_count,
        "total_hospitals": total_hospitals
    }

    return render_template(
        "dashboard.html",
        user=user,
        stats=stats,
        referrals=referrals,
        medicines=medicines,
        teleconsults=teleconsults,
        high_risk_cases=high_risk_cases,
        patient_teleconsults=patient_teleconsults,
        patient_prescriptions=patient_prescriptions,
        nearby_hospitals=nearby_hospitals
    )


@main_bp.route("/records")
@login_required
def records_page():
    """Longitudinal Patient Records / ABHA Unified Medical Journey."""
    default_abha = session.get("abha_id") or "91-3321-4451-0982"
    abha_query = request.args.get("abha", default_abha).strip()
    return render_template("records.html", active_abha=abha_query)


@main_bp.route("/analytics")
def analytics_page():
    """Public Health Facility Quality & Impact Dashboard."""
    return render_template("analytics.html")

