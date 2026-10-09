from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import teleconsult as tc_model
from middleware.auth_middleware import login_required
from middleware.csrf import protect

teleconsult_bp = Blueprint("teleconsult", __name__)


# =====================================================================
# TELECONSULT ROUTES: QUEUE & ACTIONS
# =====================================================================

@teleconsult_bp.route("/teleconsult", methods=["GET", "POST"])
@login_required
@protect
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

        tc_model.create(
            patient_name, abha_id or f"91-{datetime.now().strftime('%m%d')}-0000-0000",
            age, gender, session.get("user_name", "Frontline Worker"),
            "Dr. Rajesh Sharma (MO Bilaspur)", specialty,
            chief_complaint, vitals, priority
        )
        flash(f"Patient {patient_name} added to Tele-OPD Queue with priority: {priority}.", "success")
        return redirect(url_for("teleconsult"))

    queue = tc_model.list_queue()
    return render_template("teleconsult.html", queue=queue)


@teleconsult_bp.route("/api/teleconsult/<int:tc_id>/update", methods=["POST"])
@login_required
@protect
def api_teleconsult_update(tc_id):
    """Update teleconsult status and prescription."""
    data = request.get_json() or {}
    status = data.get("status", "").strip()
    prescription = data.get("prescription", "").strip()

    if status and status not in ("In-Queue", "In-Session", "Completed"):
        return jsonify({"success": False, "error": "Invalid status value"}), 400

    if not tc_model.exists(tc_id):
        return jsonify({"success": False, "error": "Teleconsult not found"}), 404

    fields = {}
    if status:
        fields["status"] = status
    if prescription:
        fields["prescription"] = prescription

    tc_model.update(tc_id, fields)

    return jsonify({"success": True, "message": f"Teleconsult #{tc_id} updated"})


@teleconsult_bp.route("/api/teleconsult/<int:tc_id>/delete", methods=["POST"])
@login_required
@protect
def api_teleconsult_delete(tc_id):
    """Remove teleconsult record from queue."""
    if not tc_model.exists(tc_id):
        return jsonify({"success": False, "error": "Teleconsult not found"}), 404

    tc_model.delete(tc_id)
    return jsonify({"success": True, "message": f"Teleconsult #{tc_id} removed from queue"})

