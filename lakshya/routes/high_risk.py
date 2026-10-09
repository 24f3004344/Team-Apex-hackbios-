from flask import Blueprint, render_template, request, jsonify
from db import get_db

high_risk_bp = Blueprint("high_risk", __name__)


# =====================================================================
# HIGH-RISK CARE ROUTES: SURVEILLANCE & ACTIONS
# =====================================================================

@high_risk_bp.route("/high-risk")
def high_risk_page():
    """High-Risk Patient Follow-up for Maternal, Child & Chronic Conditions."""
    db = get_db()
    cases = db.execute(
        "SELECT * FROM high_risk_cases ORDER BY CASE status WHEN 'Critical' THEN 1 WHEN 'Due Today' THEN 2 ELSE 3 END, id ASC"
    ).fetchall()
    return render_template("high_risk.html", cases=cases)


@high_risk_bp.route("/api/high-risk/<int:case_id>/update", methods=["POST"])
def api_high_risk_update(case_id):
    """Update high-risk case status, notes, or next action date."""
    data = request.get_json() or {}
    status = data.get("status", "").strip()
    notes = data.get("notes", "").strip()
    next_action_date = data.get("next_action_date", "").strip()

    if status and status not in ("Monitored", "Due Today", "Critical"):
        return jsonify({"success": False, "error": "Invalid status"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM high_risk_cases WHERE id = ?", (case_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "High-risk case not found"}), 404

    updates, params = [], []
    if status:
        updates.append("status = ?")
        params.append(status)
    if notes:
        updates.append("notes = ?")
        params.append(notes)
    if next_action_date:
        updates.append("next_action_date = ?")
        params.append(next_action_date)

    if updates:
        params.append(case_id)
        db.execute(f"UPDATE high_risk_cases SET {', '.join(updates)} WHERE id = ?", params)
        db.commit()

    return jsonify({"success": True, "message": f"High-risk case #{case_id} updated"})


@high_risk_bp.route("/api/high-risk/<int:case_id>/delete", methods=["POST"])
def api_high_risk_delete(case_id):
    """Remove a high-risk case record."""
    db = get_db()
    existing = db.execute("SELECT id FROM high_risk_cases WHERE id = ?", (case_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "High-risk case not found"}), 404

    db.execute("DELETE FROM high_risk_cases WHERE id = ?", (case_id,))
    db.commit()
    return jsonify({"success": True, "message": f"High-risk case #{case_id} removed"})

