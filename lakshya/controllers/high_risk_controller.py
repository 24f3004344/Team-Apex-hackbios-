from flask import Blueprint, render_template, request, jsonify
from models import high_risk_case as hr_model
from middleware.auth_middleware import login_required

high_risk_bp = Blueprint("high_risk", __name__)


# =====================================================================
# HIGH-RISK CARE ROUTES: SURVEILLANCE & ACTIONS
# =====================================================================

@high_risk_bp.route("/high-risk")
@login_required
def high_risk_page():
    """High-Risk Patient Follow-up for Maternal, Child & Chronic Conditions."""
    cases = hr_model.list_all()
    return render_template("high_risk.html", cases=cases)


@high_risk_bp.route("/api/high-risk/<int:case_id>/update", methods=["POST"])
@login_required
def api_high_risk_update(case_id):
    """Update high-risk case status, notes, or next action date."""
    data = request.get_json() or {}
    status = data.get("status", "").strip()
    notes = data.get("notes", "").strip()
    next_action_date = data.get("next_action_date", "").strip()

    if status and status not in ("Monitored", "Due Today", "Critical"):
        return jsonify({"success": False, "error": "Invalid status"}), 400

    if not hr_model.exists(case_id):
        return jsonify({"success": False, "error": "High-risk case not found"}), 404

    fields = {}
    if status:
        fields["status"] = status
    if notes:
        fields["notes"] = notes
    if next_action_date:
        fields["next_action_date"] = next_action_date

    hr_model.update(case_id, fields)

    return jsonify({"success": True, "message": f"High-risk case #{case_id} updated"})


@high_risk_bp.route("/api/high-risk/<int:case_id>/delete", methods=["POST"])
@login_required
def api_high_risk_delete(case_id):
    """Remove a high-risk case record."""
    if not hr_model.exists(case_id):
        return jsonify({"success": False, "error": "High-risk case not found"}), 404

    hr_model.delete(case_id)
    return jsonify({"success": True, "message": f"High-risk case #{case_id} removed"})

