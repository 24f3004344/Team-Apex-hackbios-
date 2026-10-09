from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from middleware.auth_middleware import login_required

triage_bp = Blueprint("triage", __name__)


# =====================================================================
# CLINICAL TRIAGE ROUTES: SCREENER & EVALUATOR
# =====================================================================

@triage_bp.route("/triage")
@login_required
def triage_page():
    """Comprehensive Digital Clinical Triage & Emergency Escalation Hub."""
    return render_template("triage.html")


@triage_bp.route("/api/triage-evaluate", methods=["POST"])
def api_triage_evaluate():
    """Evaluate patient clinical signs and return triage tier and escalation actions."""
    data = request.get_json() or {}
    fever = data.get("fever", False)
    breathing = data.get("breathing_difficulty", False)
    systolic_bp = int(data.get("systolic_bp", 120))
    maternal_weeks = int(data.get("maternal_weeks", 0))
    pediatric_age = int(data.get("pediatric_age", 99))

    if breathing or (maternal_weeks > 20 and systolic_bp >= 160) or (pediatric_age < 5 and fever and breathing):
        tier = "Red - Emergency Escalation"
        action = "Immediate 108 Ambulance Dispatch & Alert District Emergency Hub. Keep patient in recovery posture."
        badge = "emergency"
        facility = "Sub-Divisional Hospital / District Emergency"
    elif systolic_bp >= 140 or fever or (maternal_weeks > 0 and systolic_bp >= 135):
        tier = "Yellow - Priority Tele-Consultation"
        action = "Schedule Assisted Tele-OPD within 4 hours. Connect with Medical Officer at Primary Health Centre."
        badge = "urgent"
        facility = "Primary Health Centre (PHC Tele-OPD)"
    else:
        tier = "Green - Routine Primary Care & Counseling"
        action = "Manage at Sub-Centre via ASHA/ANM protocol. Dispense essential supplements and schedule follow-up."
        badge = "routine"
        facility = "Health & Wellness Sub-Centre"

    return jsonify({
        "tier": tier,
        "action": action,
        "badge": badge,
        "facility": facility,
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    })

