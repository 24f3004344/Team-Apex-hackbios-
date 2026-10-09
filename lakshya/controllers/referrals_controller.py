from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from models import referral as ref_model
from middleware.auth_middleware import login_required
from middleware.csrf import protect

referrals_bp = Blueprint("referrals", __name__)


# =====================================================================
# REFERRAL ROUTES: PIPELINE & ACTIONS
# =====================================================================

@referrals_bp.route("/referrals", methods=["GET", "POST"])
@login_required
@protect
def referrals_page():
    """Closed-Loop Referral Tracking & Inter-Facility Handover."""
    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        abha_id = request.form.get("abha_id", "").strip()
        source_facility = request.form.get("source_facility", "").strip()
        target_facility = request.form.get("target_facility", "").strip()
        specialty = request.form.get("specialty", "").strip()
        urgency = request.form.get("urgency", "Urgent").strip()
        notes = request.form.get("notes", "").strip()

        if not patient_name or not source_facility or not target_facility or not specialty:
            flash("Patient name, source/target facility, and specialty are all required.", "danger")
            return redirect(url_for("referrals_page"))

        if urgency not in ("Normal", "Urgent", "Emergency"):
            urgency = "Urgent"

        ref_model.create(
            patient_name, abha_id or f"91-{datetime.now().strftime('%m%d')}-0000-0000",
            source_facility, target_facility, specialty, urgency, notes
        )
        flash(f"Referral successfully initiated for {patient_name} to {target_facility}!", "success")
        return redirect(url_for("referrals_page"))

    referrals = ref_model.list_all()
    return render_template("referrals.html", referrals=referrals)


@referrals_bp.route("/api/referral/<int:ref_id>/update", methods=["POST"])
@login_required
@protect
def api_referral_update(ref_id):
    """Update referral progress status."""
    data = request.get_json() or {}
    new_status = data.get("status", "").strip()

    if new_status not in ("Initiated", "In-Transit", "Consulted", "Closed"):
        return jsonify({"success": False, "error": "Invalid status. Must be Initiated, In-Transit, Consulted, or Closed."}), 400

    if not ref_model.exists(ref_id):
        return jsonify({"success": False, "error": "Referral not found"}), 404

    ref_model.update_status(ref_id, new_status)
    return jsonify({"success": True, "message": f"Referral #{ref_id} status updated to {new_status}"})


@referrals_bp.route("/api/referral/<int:ref_id>/delete", methods=["POST"])
@login_required
@protect
def api_referral_delete(ref_id):
    """Delete a referral."""
    if not ref_model.exists(ref_id):
        return jsonify({"success": False, "error": "Referral not found"}), 404

    ref_model.delete(ref_id)
    return jsonify({"success": True, "message": f"Referral #{ref_id} deleted"})

