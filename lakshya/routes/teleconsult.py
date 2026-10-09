from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from db import get_db
from auth_middleware import login_required, role_required

teleconsult_bp = Blueprint("teleconsult", __name__)


# =====================================================================
# TELECONSULT ROUTES: QUEUE & ACTIONS
# =====================================================================

@teleconsult_bp.route("/teleconsult", methods=["GET", "POST"])
@role_required("doctor", "frontline")
def teleconsult():
    """Assisted Teleconsultation & Tele-OPD Hub."""
    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        abha_id = request.form.get("abha_id", "").strip()
        age = request.form.get("age", 30, type=int)
        gender = request.form.get("gender", "Female")
        specialty = request.form.get("specialty", "General Medicine")
        chief_complaint = request.form.get("chief_complaint", "").strip()
        vitals = request.form.get("vitals", "BP: 120/80").strip()
        priority = request.form.get("priority", "Routine")

        if not patient_name or not chief_complaint:
            flash("Patient name and chief complaint are required.", "danger")
            return redirect(url_for("teleconsult"))

        if priority not in ("Routine", "Priority", "Emergency"):
            priority = "Routine"

        db = get_db()
        db.execute("""
            INSERT INTO teleconsults (patient_name, abha_id, age, gender, asha_worker, doctor_name, specialty, chief_complaint, vitals, priority, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'In-Queue')
        """, (
            patient_name, abha_id or f"91-{datetime.now().strftime('%m%d')}-0000-0000",
            age, gender, session.get("user_name", "Frontline Worker"),
            "Dr. Rajesh Sharma (MO Bilaspur)", specialty,
            chief_complaint, vitals, priority
        ))
        db.commit()
        flash(f"Patient {patient_name} added to Tele-OPD Queue with priority: {priority}.", "success")
        return redirect(url_for("teleconsult"))

    db = get_db()
    queue = db.execute(
        "SELECT * FROM teleconsults ORDER BY CASE priority WHEN 'Emergency' THEN 1 WHEN 'Priority' THEN 2 ELSE 3 END, id DESC"
    ).fetchall()
    return render_template("teleconsult.html", queue=queue)


@teleconsult_bp.route("/api/teleconsult/<int:tc_id>/update", methods=["POST"])
@role_required("doctor", "frontline")
def api_teleconsult_update(tc_id):
    """Update teleconsult status and prescription."""
    data = request.get_json() or {}
    status = data.get("status", "").strip()
    prescription = data.get("prescription", "").strip()

    if status and status not in ("In-Queue", "In-Session", "Completed"):
        return jsonify({"success": False, "error": "Invalid status value"}), 400

    db = get_db()
    existing = db.execute("SELECT id FROM teleconsults WHERE id = ?", (tc_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "Teleconsult not found"}), 404

    updates, params = [], []
    if status:
        updates.append("status = ?")
        params.append(status)
    if prescription:
        updates.append("prescription = ?")
        params.append(prescription)

    if updates:
        params.append(tc_id)
        db.execute(f"UPDATE teleconsults SET {', '.join(updates)} WHERE id = ?", params)
        db.commit()

    return jsonify({"success": True, "message": f"Teleconsult #{tc_id} updated"})


@teleconsult_bp.route("/api/teleconsult/<int:tc_id>/delete", methods=["POST"])
@role_required("doctor", "frontline")
def api_teleconsult_delete(tc_id):
    """Remove teleconsult record from queue."""
    db = get_db()
    existing = db.execute("SELECT id FROM teleconsults WHERE id = ?", (tc_id,)).fetchone()
    if not existing:
        return jsonify({"success": False, "error": "Teleconsult not found"}), 404

    db.execute("DELETE FROM teleconsults WHERE id = ?", (tc_id,))
    db.commit()
    return jsonify({"success": True, "message": f"Teleconsult #{tc_id} removed from queue"})

