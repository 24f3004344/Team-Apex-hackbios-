from datetime import datetime
from flask import Blueprint, render_template, request, jsonify
from models import medicine as med_model
from models import diagnostic as diag_model
from middleware.auth_middleware import login_required
from middleware.csrf import protect

inventory_bp = Blueprint("inventory", __name__)


# =====================================================================
# INVENTORY ROUTES: MEDICINES & DIAGNOSTICS
# =====================================================================

@inventory_bp.route("/inventory")
@login_required
def inventory_page():
    """Live Medicine & Diagnostic Tests Inventory Management."""
    medicines = med_model.list_all()
    diagnostics = diag_model.list_all()
    return render_template("inventory.html", medicines=medicines, diagnostics=diagnostics)


@inventory_bp.route("/api/medicine/<int:med_id>/update", methods=["POST"])
@login_required
@protect
def api_medicine_update(med_id):
    """Update medicine stock quantity and status."""
    data = request.get_json() or {}
    units = data.get("units")
    stock_status = data.get("stock_status", "").strip()

    if not med_model.exists(med_id):
        return jsonify({"success": False, "error": "Medicine not found"}), 404

    fields = {}
    if units is not None:
        try:
            units = int(units)
        except (TypeError, ValueError):
            return jsonify({"success": False, "error": "units must be a number"}), 400
        fields["units"] = units
        # Auto-compute stock_status from units if not explicitly provided
        if not stock_status:
            if units == 0:
                stock_status = "Out of Stock"
            elif units < 50:
                stock_status = "Low Stock"
            else:
                stock_status = "Available"

    if stock_status:
        if stock_status not in ("Available", "Low Stock", "Out of Stock"):
            return jsonify({"success": False, "error": "Invalid stock_status"}), 400
        fields["stock_status"] = stock_status

    fields["last_updated"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
    med_model.update(med_id, fields)

    return jsonify({"success": True, "message": f"Medicine #{med_id} stock updated"})


@inventory_bp.route("/api/medicine/<int:med_id>/delete", methods=["POST"])
@login_required
@protect
def api_medicine_delete(med_id):
    """Delete a medicine entry from inventory."""
    if not med_model.exists(med_id):
        return jsonify({"success": False, "error": "Medicine not found"}), 404

    med_model.delete(med_id)
    return jsonify({"success": True, "message": f"Medicine #{med_id} removed from inventory"})


@inventory_bp.route("/api/medicine-search")
def api_medicine_search():
    """Live search API for medicines by name, category, and district."""
    query = request.args.get("q", "").strip()
    district = request.args.get("district", "").strip()

    results = med_model.search(query, district)

    return jsonify({"success": True, "count": len(results), "medicines": results})

